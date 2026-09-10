-- BT2 runtime / operation identity cross-binding V1.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.
-- Closes one-0158 identity seams without inventing session-to-session continuity.

-- A runtime session is one execution instance of one durable logical agent.
ALTER TABLE bt2.runtime_sessions
  ADD CONSTRAINT runtime_sessions_id_agent_uniq UNIQUE (runtime_session_id,agent_key);

-- Restore provenance must remain within the same durable agent identity.
ALTER TABLE bt2.runtime_sessions
  DROP CONSTRAINT IF EXISTS runtime_sessions_restored_from_checkpoint_id_fkey;
ALTER TABLE bt2.runtime_sessions
  ADD CONSTRAINT runtime_sessions_restore_same_agent_fkey
  FOREIGN KEY (restored_from_checkpoint_id,agent_key)
  REFERENCES bt2.operational_checkpoints(checkpoint_id,agent_key);

-- Operation actor/session provenance may be omitted, but when a runtime session is supplied
-- it must belong to the same durable logical actor.
ALTER TABLE bt2.operations
  DROP CONSTRAINT IF EXISTS operations_actor_runtime_session_id_fkey;
ALTER TABLE bt2.operations
  ADD CONSTRAINT operations_runtime_requires_actor_check
  CHECK (actor_runtime_session_id IS NULL OR actor_agent_key IS NOT NULL);
ALTER TABLE bt2.operations
  ADD CONSTRAINT operations_actor_runtime_same_agent_fkey
  FOREIGN KEY (actor_runtime_session_id,actor_agent_key)
  REFERENCES bt2.runtime_sessions(runtime_session_id,agent_key);

-- Events have their own actor identity because reconciliation may legitimately be performed
-- by an agent other than the original operation actor. Runtime provenance, when present,
-- is cross-bound to that event actor rather than inferred through the operation row.
ALTER TABLE bt2.operation_events
  ADD COLUMN actor_agent_key text;

UPDATE bt2.operation_events e
SET actor_agent_key=COALESCE(rs.agent_key,o.actor_agent_key)
FROM bt2.operations o
LEFT JOIN bt2.runtime_sessions rs ON rs.runtime_session_id=e.runtime_session_id
WHERE o.operation_id=e.operation_id;

ALTER TABLE bt2.operation_events
  ADD CONSTRAINT operation_events_actor_agent_key_fkey
  FOREIGN KEY (actor_agent_key) REFERENCES bt2.agents(agent_key);
ALTER TABLE bt2.operation_events
  ADD CONSTRAINT operation_events_runtime_requires_actor_check
  CHECK (runtime_session_id IS NULL OR actor_agent_key IS NOT NULL);
ALTER TABLE bt2.operation_events
  ADD CONSTRAINT operation_events_actor_runtime_same_agent_fkey
  FOREIGN KEY (runtime_session_id,actor_agent_key)
  REFERENCES bt2.runtime_sessions(runtime_session_id,agent_key);

-- Explicit event-actor API. A RECONCILED event must identify the reconciler.
CREATE OR REPLACE FUNCTION bt2.append_operation_event_v2(
  p_operation_id uuid,
  p_previous_event_id uuid,
  p_state text,
  p_actor_agent_key text,
  p_runtime_session_id uuid,
  p_recovery_instruction text,
  p_result_summary text DEFAULT NULL,
  p_result_payload jsonb DEFAULT NULL,
  p_effect_receipt jsonb DEFAULT NULL
) RETURNS uuid
LANGUAGE plpgsql AS $function$
DECLARE
  v_op record; v_prev record; v_event uuid:=gen_random_uuid();
  v_next integer; v_state text:=upper(btrim(p_state)); v_result_digest text;
BEGIN
  SELECT * INTO STRICT v_op FROM bt2.operations
  WHERE operation_id=p_operation_id FOR UPDATE;
  SELECT * INTO STRICT v_prev FROM bt2.operation_events
  WHERE operation_event_id=v_op.latest_event_id AND operation_id=p_operation_id;

  IF p_previous_event_id IS DISTINCT FROM v_prev.operation_event_id THEN
    RAISE EXCEPTION 'STALE_OPERATION_EVENT';
  END IF;
  IF NOT (
    (v_prev.state='PREPARED' AND v_state IN ('ATTEMPTED','FAILED','AMBIGUOUS')) OR
    (v_prev.state='ATTEMPTED' AND v_state IN ('VERIFIED','FAILED','AMBIGUOUS')) OR
    (v_prev.state='AMBIGUOUS' AND v_state='RECONCILED')
  ) THEN
    RAISE EXCEPTION 'INVALID_OPERATION_TRANSITION';
  END IF;
  IF v_state='RECONCILED' AND p_actor_agent_key IS NULL THEN
    RAISE EXCEPTION 'RECONCILIATION_REQUIRES_EXPLICIT_ACTOR';
  END IF;
  IF v_state IN ('VERIFIED','RECONCILED')
     AND (p_effect_receipt IS NULL OR p_result_summary IS NULL) THEN
    RAISE EXCEPTION 'VERIFIED_EFFECT_REQUIRES_RECEIPT';
  END IF;
  IF p_recovery_instruction NOT IN ('inspect_before_retry','no_retry_required') THEN
    RAISE EXCEPTION 'INVALID_RECOVERY_INSTRUCTION';
  END IF;

  v_next:=v_prev.sequence+1;
  IF p_result_payload IS NOT NULL THEN
    v_result_digest:=encode(digest(convert_to(p_result_payload::text,'UTF8'),'sha256'),'hex');
  END IF;

  INSERT INTO bt2.operation_events(
    operation_event_id,operation_id,sequence,state,previous_event_id,
    actor_agent_key,runtime_session_id,recovery_instruction,
    result_summary,result_payload,result_digest_sha256,effect_receipt
  ) VALUES(
    v_event,p_operation_id,v_next,v_state,v_prev.operation_event_id,
    p_actor_agent_key,p_runtime_session_id,p_recovery_instruction,
    p_result_summary,p_result_payload,v_result_digest,p_effect_receipt
  );

  UPDATE bt2.operations
  SET state=v_state,
      latest_event_id=v_event,
      attempted_at=CASE WHEN v_state='ATTEMPTED' AND attempted_at IS NULL THEN clock_timestamp() ELSE attempted_at END,
      resolved_at=CASE WHEN v_state IN ('VERIFIED','FAILED','RECONCILED') THEN clock_timestamp() ELSE resolved_at END,
      result_payload=COALESCE(p_result_payload,result_payload),
      result_digest_sha256=COALESCE(v_result_digest,result_digest_sha256),
      effect_receipt=COALESCE(p_effect_receipt,effect_receipt),
      result_summary=COALESCE(p_result_summary,result_summary),
      do_not_repeat=(v_state<>'FAILED'),
      updated_at=clock_timestamp()
  WHERE operation_id=p_operation_id;

  RETURN v_event;
END
$function$;

-- Compatibility API: preserve existing callers while deriving an explicit event actor.
CREATE OR REPLACE FUNCTION bt2.append_operation_event_v1(
  p_operation_id uuid,
  p_previous_event_id uuid,
  p_state text,
  p_runtime_session_id uuid,
  p_recovery_instruction text,
  p_result_summary text DEFAULT NULL,
  p_result_payload jsonb DEFAULT NULL,
  p_effect_receipt jsonb DEFAULT NULL
) RETURNS uuid
LANGUAGE plpgsql AS $function$
DECLARE v_actor text;
BEGIN
  IF p_runtime_session_id IS NOT NULL THEN
    SELECT rs.agent_key INTO STRICT v_actor
    FROM bt2.runtime_sessions rs
    WHERE rs.runtime_session_id=p_runtime_session_id;
  ELSE
    SELECT o.actor_agent_key INTO v_actor
    FROM bt2.operations o WHERE o.operation_id=p_operation_id;
  END IF;

  RETURN bt2.append_operation_event_v2(
    p_operation_id,p_previous_event_id,p_state,v_actor,p_runtime_session_id,
    p_recovery_instruction,p_result_summary,p_result_payload,p_effect_receipt
  );
END
$function$;

-- Operation identity digest now binds runtime provenance as well as durable actor identity.
CREATE OR REPLACE FUNCTION bt2.prepare_operation_v1(
  p_operation_id uuid,
  p_workspace_id uuid,
  p_actor_agent_key text,
  p_actor_runtime_session_id uuid,
  p_operation_kind text,
  p_target_locator text,
  p_idempotency_key text,
  p_request_payload jsonb
) RETURNS uuid
LANGUAGE plpgsql AS $function$
DECLARE v_subject jsonb; v_digest text; v_existing record; v_event uuid:=gen_random_uuid();
BEGIN
  PERFORM pg_advisory_xact_lock(hashtextextended(p_operation_id::text,0));
  IF p_request_payload IS NULL THEN RAISE EXCEPTION 'INVALID_REQUEST_PAYLOAD'; END IF;

  v_subject:=jsonb_build_object(
    'workspace_id',p_workspace_id,
    'actor_agent_key',p_actor_agent_key,
    'actor_runtime_session_id',p_actor_runtime_session_id,
    'operation_kind',p_operation_kind,
    'target_locator',p_target_locator,
    'idempotency_key',p_idempotency_key,
    'request_payload',p_request_payload
  );
  v_digest:=encode(digest(convert_to(v_subject::text,'UTF8'),'sha256'),'hex');

  SELECT * INTO v_existing FROM bt2.operations WHERE operation_id=p_operation_id;
  IF FOUND THEN
    IF v_existing.request_digest_sha256<>v_digest THEN
      RAISE EXCEPTION 'OPERATION_ID_REUSE_CONFLICT';
    END IF;
    RETURN v_existing.latest_event_id;
  END IF;

  INSERT INTO bt2.operations(
    operation_id,workspace_id,actor_agent_key,actor_runtime_session_id,
    operation_kind,target_locator,idempotency_key,request_digest_sha256,
    request_payload,state,latest_event_id,do_not_repeat
  ) VALUES(
    p_operation_id,p_workspace_id,p_actor_agent_key,p_actor_runtime_session_id,
    p_operation_kind,p_target_locator,p_idempotency_key,v_digest,
    p_request_payload,'PREPARED',v_event,true
  );

  INSERT INTO bt2.operation_events(
    operation_event_id,operation_id,sequence,state,previous_event_id,
    actor_agent_key,runtime_session_id,recovery_instruction
  ) VALUES(
    v_event,p_operation_id,1,'PREPARED',NULL,
    p_actor_agent_key,p_actor_runtime_session_id,'inspect_before_retry'
  );
  RETURN v_event;
END
$function$;

-- Deliberate design choice: runtime-session continuity is represented through
-- same-agent checkpoint restoration and explicit handoff provenance. No predecessor-
-- session edge is added because sessions are replaceable execution instances, not a
-- durable identity chain.
