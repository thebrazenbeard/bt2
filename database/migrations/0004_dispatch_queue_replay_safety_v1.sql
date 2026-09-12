-- BT2 canonical dispatch hardening V1.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.
-- Preserves the existing queue projection while adding durable event and claim receipts.

-- 1. Projection fields required for replay safety.
ALTER TABLE bt2.work_queue ADD COLUMN enqueue_key text;
ALTER TABLE bt2.work_queue ADD COLUMN enqueue_request_digest_sha256 text;
ALTER TABLE bt2.work_queue ADD COLUMN claim_generation bigint NOT NULL DEFAULT 0;
ALTER TABLE bt2.work_queue ADD COLUMN latest_event_id uuid;
ALTER TABLE bt2.work_queue
  ADD CONSTRAINT work_queue_enqueue_request_digest_sha256_check
  CHECK (enqueue_request_digest_sha256 IS NULL OR enqueue_request_digest_sha256 ~ '^[0-9a-f]{64}$');
ALTER TABLE bt2.work_queue
  ADD CONSTRAINT work_queue_claim_generation_check CHECK (claim_generation>=0);
CREATE UNIQUE INDEX work_queue_enqueue_key_v2
  ON bt2.work_queue(queue_name,enqueue_key)
  WHERE enqueue_key IS NOT NULL;

-- Existing terminal rows may retain stale lease identity from the V1 ACK path.
-- Clear only projection metadata; claim history is not fabricated.
UPDATE bt2.work_queue
SET lease_token=NULL, lease_owner=NULL, lease_until=NULL
WHERE state<>'CLAIMED';

-- 2. Durable append-only queue transition history.
CREATE TABLE bt2.work_queue_events (
  queue_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  queue_item_id uuid NOT NULL REFERENCES bt2.work_queue(queue_item_id),
  event_sequence integer NOT NULL CHECK (event_sequence>=1),
  event_type text NOT NULL CHECK (event_type IN ('MIGRATED_SNAPSHOT','ENQUEUED','CLAIMED','ACKED','RELEASED','DEAD','CANCELLED')),
  resulting_state text NOT NULL CHECK (resulting_state IN ('READY','CLAIMED','ACKED','DEAD','CANCELLED')),
  previous_event_id uuid,
  claim_generation bigint NOT NULL CHECK (claim_generation>=0),
  lease_token uuid,
  lease_owner text,
  action_digest_sha256 text CHECK (action_digest_sha256 IS NULL OR action_digest_sha256 ~ '^[0-9a-f]{64}$'),
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT work_queue_events_root_check CHECK ((event_sequence=1)=(previous_event_id IS NULL)),
  CONSTRAINT work_queue_events_item_sequence_uniq UNIQUE (queue_item_id,event_sequence),
  CONSTRAINT work_queue_events_id_item_uniq UNIQUE (queue_event_id,queue_item_id),
  CONSTRAINT work_queue_events_id_item_state_uniq UNIQUE (queue_event_id,queue_item_id,resulting_state),
  CONSTRAINT work_queue_events_one_successor_uniq UNIQUE (previous_event_id),
  CONSTRAINT work_queue_events_same_item_predecessor_fkey
    FOREIGN KEY (previous_event_id,queue_item_id)
    REFERENCES bt2.work_queue_events(queue_event_id,queue_item_id)
);
CREATE UNIQUE INDEX work_queue_events_one_root_per_item_v1
  ON bt2.work_queue_events(queue_item_id) WHERE previous_event_id IS NULL;
CREATE TRIGGER work_queue_events_append_only_v1
BEFORE UPDATE OR DELETE ON bt2.work_queue_events
FOR EACH ROW EXECUTE FUNCTION bt2.prevent_append_only_history_mutation_v1();

-- Honest migration roots for rows that predate queue event history.
WITH roots AS (
  INSERT INTO bt2.work_queue_events(
    queue_item_id,event_sequence,event_type,resulting_state,previous_event_id,
    claim_generation,lease_token,lease_owner,details
  )
  SELECT q.queue_item_id,1,'MIGRATED_SNAPSHOT',q.state,NULL,
         q.claim_generation,NULL,NULL,
         jsonb_build_object(
           'historical_projection_only',true,
           'created_at',q.created_at,
           'claimed_at',q.claimed_at,
           'acked_at',q.acked_at,
           'claim_count',q.claim_count,
           'payload_digest_sha256',q.payload_digest_sha256
         )
  FROM bt2.work_queue q
  RETURNING queue_event_id,queue_item_id
)
UPDATE bt2.work_queue q
SET latest_event_id=r.queue_event_id
FROM roots r
WHERE q.queue_item_id=r.queue_item_id;

ALTER TABLE bt2.work_queue ALTER COLUMN latest_event_id SET NOT NULL;
ALTER TABLE bt2.work_queue
  ADD CONSTRAINT work_queue_latest_event_projection_fkey
  FOREIGN KEY (latest_event_id,queue_item_id,state)
  REFERENCES bt2.work_queue_events(queue_event_id,queue_item_id,resulting_state)
  DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE bt2.work_queue
  ADD CONSTRAINT work_queue_lease_shape_check
  CHECK (
    (state='CLAIMED' AND lease_token IS NOT NULL AND lease_owner IS NOT NULL AND lease_until IS NOT NULL)
    OR
    (state<>'CLAIMED' AND lease_token IS NULL AND lease_owner IS NULL AND lease_until IS NULL)
  );
ALTER TABLE bt2.work_queue
  ADD CONSTRAINT work_queue_ack_shape_check
  CHECK (state<>'ACKED' OR acked_at IS NOT NULL);

-- 3. Durable claim-request receipts make claim response loss replayable without renewing authority.
CREATE TABLE bt2.work_claim_requests (
  claim_request_id uuid PRIMARY KEY,
  queue_name text NOT NULL,
  target_agent_key text REFERENCES bt2.agents(agent_key),
  lease_owner text NOT NULL,
  lease_seconds integer NOT NULL CHECK (lease_seconds BETWEEN 1 AND 86400),
  requested_qty integer NOT NULL CHECK (requested_qty BETWEEN 1 AND 100),
  request_digest_sha256 text NOT NULL CHECK (request_digest_sha256 ~ '^[0-9a-f]{64}$'),
  created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE bt2.work_claim_items (
  claim_request_id uuid NOT NULL REFERENCES bt2.work_claim_requests(claim_request_id),
  ordinal integer NOT NULL CHECK (ordinal>=1),
  queue_item_id uuid NOT NULL REFERENCES bt2.work_queue(queue_item_id),
  claim_generation bigint NOT NULL CHECK (claim_generation>=1),
  lease_token uuid NOT NULL,
  lease_until timestamptz NOT NULL,
  PRIMARY KEY (claim_request_id,ordinal),
  UNIQUE (claim_request_id,queue_item_id),
  UNIQUE (queue_item_id,claim_generation)
);
CREATE TRIGGER work_claim_requests_append_only_v1
BEFORE UPDATE OR DELETE ON bt2.work_claim_requests
FOR EACH ROW EXECUTE FUNCTION bt2.prevent_append_only_history_mutation_v1();
CREATE TRIGGER work_claim_items_append_only_v1
BEFORE UPDATE OR DELETE ON bt2.work_claim_items
FOR EACH ROW EXECUTE FUNCTION bt2.prevent_append_only_history_mutation_v1();

-- 4. Replay-safe enqueue. Caller supplies the durable idempotency subject.
CREATE OR REPLACE FUNCTION bt2.enqueue_work_v2(
  p_enqueue_key text,
  p_queue_name text,
  p_source_agent_key text,
  p_target_agent_key text,
  p_work_kind text,
  p_payload jsonb,
  p_priority integer DEFAULT 100,
  p_available_at timestamptz DEFAULT NULL
) RETURNS TABLE(out_queue_item_id uuid,idempotent_replay boolean)
LANGUAGE plpgsql AS $function$
DECLARE
  v_key text:=btrim(p_enqueue_key);
  v_queue text:=btrim(p_queue_name);
  v_kind text:=btrim(p_work_kind);
  v_request jsonb;
  v_digest text;
  v_existing record;
  v_item uuid:=gen_random_uuid();
  v_event uuid:=gen_random_uuid();
  v_available timestamptz:=coalesce(p_available_at,clock_timestamp());
BEGIN
  IF v_key IS NULL OR v_key='' THEN RAISE EXCEPTION 'INVALID_ENQUEUE_KEY'; END IF;
  IF v_queue IS NULL OR v_queue='' THEN RAISE EXCEPTION 'INVALID_QUEUE_NAME'; END IF;
  IF v_kind IS NULL OR v_kind='' THEN RAISE EXCEPTION 'INVALID_WORK_KIND'; END IF;
  IF p_payload IS NULL THEN RAISE EXCEPTION 'INVALID_PAYLOAD'; END IF;
  v_request:=jsonb_build_object(
    'queue_name',v_queue,'source_agent_key',p_source_agent_key,
    'target_agent_key',p_target_agent_key,'work_kind',v_kind,
    'payload',p_payload,'priority',p_priority,'requested_available_at',p_available_at
  );
  v_digest:=encode(digest(convert_to(v_request::text,'UTF8'),'sha256'),'hex');
  PERFORM pg_advisory_xact_lock(hashtextextended(v_queue||E'\n'||v_key,0));
  SELECT * INTO v_existing FROM bt2.work_queue
  WHERE queue_name=v_queue AND enqueue_key=v_key;
  IF FOUND THEN
    IF v_existing.enqueue_request_digest_sha256 IS DISTINCT FROM v_digest THEN
      RAISE EXCEPTION 'ENQUEUE_KEY_REUSE_CONFLICT';
    END IF;
    RETURN QUERY SELECT v_existing.queue_item_id,true;
    RETURN;
  END IF;
  INSERT INTO bt2.work_queue(
    queue_item_id,queue_name,source_agent_key,target_agent_key,work_kind,payload,
    payload_digest_sha256,enqueue_key,enqueue_request_digest_sha256,state,priority,
    available_at,claim_generation,latest_event_id
  ) VALUES(
    v_item,v_queue,p_source_agent_key,p_target_agent_key,v_kind,p_payload,
    encode(digest(convert_to(p_payload::text,'UTF8'),'sha256'),'hex'),v_key,v_digest,'READY',p_priority,
    v_available,0,v_event
  );
  INSERT INTO bt2.work_queue_events(
    queue_event_id,queue_item_id,event_sequence,event_type,resulting_state,
    claim_generation,details
  ) VALUES(
    v_event,v_item,1,'ENQUEUED','READY',0,
    jsonb_build_object('enqueue_key',v_key,'request_digest_sha256',v_digest)
  );
  RETURN QUERY SELECT v_item,false;
END
$function$;

-- 5. Replay-safe claim. Replaying the same claim_request_id returns the exact original
-- receipt and never renews or recreates lease authority.
CREATE OR REPLACE FUNCTION bt2.claim_work_v2(
  p_claim_request_id uuid,
  p_queue_name text,
  p_target_agent_key text,
  p_lease_owner text,
  p_lease_seconds integer DEFAULT 300,
  p_qty integer DEFAULT 10
) RETURNS TABLE(
  queue_item_id uuid, work_kind text, payload jsonb, payload_digest_sha256 text,
  priority integer, claim_generation bigint, lease_token uuid, lease_until timestamptz,
  current_state text, lease_active boolean, idempotent_replay boolean
)
LANGUAGE plpgsql AS $function$
DECLARE
  v_request jsonb; v_digest text; v_existing record; v_q record;
  v_token uuid; v_event uuid; v_prev_seq integer; v_gen bigint; v_until timestamptz;
  v_ordinal integer:=0; v_replay boolean:=false;
BEGIN
  IF p_claim_request_id IS NULL THEN RAISE EXCEPTION 'INVALID_CLAIM_REQUEST_ID'; END IF;
  IF p_lease_seconds<1 OR p_lease_seconds>86400 THEN RAISE EXCEPTION 'INVALID_LEASE_SECONDS'; END IF;
  IF p_qty<1 OR p_qty>100 THEN RAISE EXCEPTION 'INVALID_QTY'; END IF;
  IF p_lease_owner IS NULL OR btrim(p_lease_owner)='' THEN RAISE EXCEPTION 'INVALID_LEASE_OWNER'; END IF;
  v_request:=jsonb_build_object(
    'queue_name',p_queue_name,'target_agent_key',p_target_agent_key,
    'lease_owner',p_lease_owner,'lease_seconds',p_lease_seconds,'qty',p_qty
  );
  v_digest:=encode(digest(convert_to(v_request::text,'UTF8'),'sha256'),'hex');
  PERFORM pg_advisory_xact_lock(hashtextextended(p_claim_request_id::text,0));
  SELECT * INTO v_existing FROM bt2.work_claim_requests WHERE claim_request_id=p_claim_request_id;
  IF FOUND THEN
    IF v_existing.request_digest_sha256<>v_digest THEN RAISE EXCEPTION 'CLAIM_REQUEST_ID_REUSE_CONFLICT'; END IF;
    v_replay:=true;
  ELSE
    INSERT INTO bt2.work_claim_requests(
      claim_request_id,queue_name,target_agent_key,lease_owner,lease_seconds,requested_qty,request_digest_sha256
    ) VALUES(p_claim_request_id,p_queue_name,p_target_agent_key,p_lease_owner,p_lease_seconds,p_qty,v_digest);
    FOR v_q IN
      SELECT q.* FROM bt2.work_queue q
      WHERE q.queue_name=p_queue_name
        AND q.target_agent_key IS NOT DISTINCT FROM p_target_agent_key
        AND q.available_at<=clock_timestamp()
        AND (q.state='READY' OR (q.state='CLAIMED' AND q.lease_until<clock_timestamp()))
      ORDER BY q.priority,q.created_at,q.queue_item_id
      FOR UPDATE SKIP LOCKED
      LIMIT p_qty
    LOOP
      v_ordinal:=v_ordinal+1;
      v_token:=gen_random_uuid();
      v_event:=gen_random_uuid();
      v_gen:=v_q.claim_generation+1;
      v_until:=clock_timestamp()+make_interval(secs=>p_lease_seconds);
      SELECT event_sequence INTO STRICT v_prev_seq FROM bt2.work_queue_events
      WHERE queue_event_id=v_q.latest_event_id;
      INSERT INTO bt2.work_queue_events(
        queue_event_id,queue_item_id,event_sequence,event_type,resulting_state,previous_event_id,
        claim_generation,lease_token,lease_owner,action_digest_sha256,details
      ) VALUES(
        v_event,v_q.queue_item_id,v_prev_seq+1,'CLAIMED','CLAIMED',v_q.latest_event_id,
        v_gen,v_token,p_lease_owner,v_digest,
        jsonb_build_object('claim_request_id',p_claim_request_id,'lease_until',v_until)
      );
      UPDATE bt2.work_queue
      SET state='CLAIMED',claim_generation=v_gen,lease_token=v_token,lease_owner=p_lease_owner,
          lease_until=v_until,claim_count=claim_count+1,claimed_at=clock_timestamp(),
          acked_at=NULL,latest_event_id=v_event
      WHERE bt2.work_queue.queue_item_id=v_q.queue_item_id;
      INSERT INTO bt2.work_claim_items(
        claim_request_id,ordinal,queue_item_id,claim_generation,lease_token,lease_until
      ) VALUES(p_claim_request_id,v_ordinal,v_q.queue_item_id,v_gen,v_token,v_until);
    END LOOP;
  END IF;
  RETURN QUERY
  SELECT q.queue_item_id,q.work_kind,q.payload,q.payload_digest_sha256,q.priority,
         i.claim_generation,i.lease_token,i.lease_until,q.state,
         (q.state='CLAIMED' AND q.claim_generation=i.claim_generation
          AND q.lease_token=i.lease_token AND q.lease_until>=clock_timestamp()),
         v_replay
  FROM bt2.work_claim_items i
  JOIN bt2.work_queue q ON q.queue_item_id=i.queue_item_id
  WHERE i.claim_request_id=p_claim_request_id
  ORDER BY i.ordinal;
END
$function$;

-- 6. ACK is replayable by the exact lease token. Terminal ACK clears lease identity.
CREATE OR REPLACE FUNCTION bt2.ack_work_v2(p_queue_item_id uuid,p_lease_token uuid)
RETURNS TABLE(acked boolean,idempotent_replay boolean)
LANGUAGE plpgsql AS $function$
DECLARE v_q record; v_prior record; v_event uuid:=gen_random_uuid(); v_seq integer; v_digest text;
BEGIN
  v_digest:=encode(digest(convert_to(jsonb_build_object('action','ACK','queue_item_id',p_queue_item_id,'lease_token',p_lease_token)::text,'UTF8'),'sha256'),'hex');
  PERFORM pg_advisory_xact_lock(hashtextextended(p_queue_item_id::text,0));
  SELECT * INTO v_prior FROM bt2.work_queue_events
  WHERE queue_item_id=p_queue_item_id AND event_type='ACKED' AND lease_token=p_lease_token
  ORDER BY event_sequence DESC LIMIT 1;
  IF FOUND THEN
    IF v_prior.action_digest_sha256<>v_digest THEN RAISE EXCEPTION 'ACK_REPLAY_CONFLICT'; END IF;
    RETURN QUERY SELECT true,true; RETURN;
  END IF;
  SELECT * INTO v_q FROM bt2.work_queue WHERE queue_item_id=p_queue_item_id FOR UPDATE;
  IF NOT FOUND OR v_q.state<>'CLAIMED' OR v_q.lease_token IS DISTINCT FROM p_lease_token
     OR v_q.lease_until<clock_timestamp() THEN RAISE EXCEPTION 'STALE_OR_INVALID_LEASE'; END IF;
  SELECT event_sequence INTO STRICT v_seq FROM bt2.work_queue_events WHERE queue_event_id=v_q.latest_event_id;
  INSERT INTO bt2.work_queue_events(
    queue_event_id,queue_item_id,event_sequence,event_type,resulting_state,previous_event_id,
    claim_generation,lease_token,lease_owner,action_digest_sha256,details
  ) VALUES(
    v_event,p_queue_item_id,v_seq+1,'ACKED','ACKED',v_q.latest_event_id,
    v_q.claim_generation,p_lease_token,v_q.lease_owner,v_digest,'{}'::jsonb
  );
  UPDATE bt2.work_queue
  SET state='ACKED',lease_token=NULL,lease_owner=NULL,lease_until=NULL,
      acked_at=clock_timestamp(),latest_event_id=v_event
  WHERE queue_item_id=p_queue_item_id;
  RETURN QUERY SELECT true,false;
END
$function$;

-- Compatibility wrapper now inherits V2 exact-lease/idempotent behavior.
CREATE OR REPLACE FUNCTION bt2.ack_work(p_queue_item_id uuid,p_lease_token uuid)
RETURNS boolean LANGUAGE plpgsql AS $function$
DECLARE v boolean;
BEGIN SELECT acked INTO STRICT v FROM bt2.ack_work_v2(p_queue_item_id,p_lease_token); RETURN v; END
$function$;

-- 7. Release/dead transition is also replayable by exact lease token + request digest.
CREATE OR REPLACE FUNCTION bt2.release_work_v2(
  p_queue_item_id uuid,p_lease_token uuid,p_error text DEFAULT NULL,
  p_retry_delay_seconds integer DEFAULT 0,p_dead boolean DEFAULT false
) RETURNS TABLE(released boolean,resulting_state text,idempotent_replay boolean)
LANGUAGE plpgsql AS $function$
DECLARE v_q record; v_prior record; v_event uuid:=gen_random_uuid(); v_seq integer;
        v_digest text; v_state text:=CASE WHEN p_dead THEN 'DEAD' ELSE 'READY' END;
BEGIN
  IF p_retry_delay_seconds<0 OR p_retry_delay_seconds>604800 THEN RAISE EXCEPTION 'INVALID_RETRY_DELAY'; END IF;
  v_digest:=encode(digest(convert_to(jsonb_build_object(
    'action','RELEASE','queue_item_id',p_queue_item_id,'lease_token',p_lease_token,
    'error',p_error,'retry_delay_seconds',p_retry_delay_seconds,'dead',p_dead
  )::text,'UTF8'),'sha256'),'hex');
  PERFORM pg_advisory_xact_lock(hashtextextended(p_queue_item_id::text,0));
  SELECT * INTO v_prior FROM bt2.work_queue_events
  WHERE queue_item_id=p_queue_item_id AND event_type IN ('RELEASED','DEAD') AND lease_token=p_lease_token
  ORDER BY event_sequence DESC LIMIT 1;
  IF FOUND THEN
    IF v_prior.action_digest_sha256<>v_digest THEN RAISE EXCEPTION 'RELEASE_REPLAY_CONFLICT'; END IF;
    RETURN QUERY SELECT true,v_prior.resulting_state,true; RETURN;
  END IF;
  SELECT * INTO v_q FROM bt2.work_queue WHERE queue_item_id=p_queue_item_id FOR UPDATE;
  IF NOT FOUND OR v_q.state<>'CLAIMED' OR v_q.lease_token IS DISTINCT FROM p_lease_token
     OR v_q.lease_until<clock_timestamp() THEN RAISE EXCEPTION 'STALE_OR_INVALID_LEASE'; END IF;
  SELECT event_sequence INTO STRICT v_seq FROM bt2.work_queue_events WHERE queue_event_id=v_q.latest_event_id;
  INSERT INTO bt2.work_queue_events(
    queue_event_id,queue_item_id,event_sequence,event_type,resulting_state,previous_event_id,
    claim_generation,lease_token,lease_owner,action_digest_sha256,details
  ) VALUES(
    v_event,p_queue_item_id,v_seq+1,CASE WHEN p_dead THEN 'DEAD' ELSE 'RELEASED' END,v_state,v_q.latest_event_id,
    v_q.claim_generation,p_lease_token,v_q.lease_owner,v_digest,
    jsonb_build_object('error',p_error,'retry_delay_seconds',p_retry_delay_seconds)
  );
  UPDATE bt2.work_queue
  SET state=v_state,
      available_at=CASE WHEN p_dead THEN available_at ELSE clock_timestamp()+make_interval(secs=>p_retry_delay_seconds) END,
      lease_token=NULL,lease_owner=NULL,lease_until=NULL,last_error=p_error,
      latest_event_id=v_event
  WHERE queue_item_id=p_queue_item_id;
  RETURN QUERY SELECT true,v_state,false;
END
$function$;

CREATE OR REPLACE FUNCTION bt2.release_work(
  p_queue_item_id uuid,p_lease_token uuid,p_error text DEFAULT NULL,
  p_retry_delay_seconds integer DEFAULT 0,p_dead boolean DEFAULT false
) RETURNS boolean LANGUAGE plpgsql AS $function$
DECLARE v boolean;
BEGIN SELECT released INTO STRICT v FROM bt2.release_work_v2(p_queue_item_id,p_lease_token,p_error,p_retry_delay_seconds,p_dead); RETURN v; END
$function$;
