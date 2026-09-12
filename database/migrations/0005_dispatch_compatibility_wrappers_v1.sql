-- Temporary compatibility wrappers for callers using the pre-V2 queue API.
-- Canonical callers should use enqueue_work_v2/claim_work_v2 with caller-owned replay keys.
-- The legacy enqueue wrapper intentionally cannot provide response-loss idempotency because
-- the old API has no caller-supplied idempotency subject.

CREATE OR REPLACE FUNCTION bt2.enqueue_work(
  p_queue_name text,
  p_source_agent_key text,
  p_target_agent_key text,
  p_work_kind text,
  p_payload jsonb,
  p_priority integer DEFAULT 100,
  p_available_at timestamptz DEFAULT clock_timestamp()
) RETURNS uuid LANGUAGE plpgsql AS $function$
DECLARE v_id uuid;
BEGIN
  SELECT out_queue_item_id INTO STRICT v_id
  FROM bt2.enqueue_work_v2(
    'legacy:'||gen_random_uuid()::text,
    p_queue_name,p_source_agent_key,p_target_agent_key,p_work_kind,
    p_payload,p_priority,p_available_at
  );
  RETURN v_id;
END
$function$;

CREATE OR REPLACE FUNCTION bt2.claim_work(
  p_queue_name text,
  p_target_agent_key text,
  p_lease_owner text,
  p_lease_seconds integer DEFAULT 300,
  p_qty integer DEFAULT 10
) RETURNS TABLE(
  queue_item_id uuid,
  work_kind text,
  payload jsonb,
  payload_digest_sha256 text,
  priority integer,
  claim_count integer,
  lease_token uuid,
  lease_until timestamptz
) LANGUAGE plpgsql AS $function$
DECLARE v_request uuid:=gen_random_uuid();
BEGIN
  RETURN QUERY
  SELECT v.queue_item_id,v.work_kind,v.payload,v.payload_digest_sha256,
         v.priority,q.claim_count,v.lease_token,v.lease_until
  FROM bt2.claim_work_v2(
    v_request,p_queue_name,p_target_agent_key,p_lease_owner,p_lease_seconds,p_qty
  ) v
  JOIN bt2.work_queue q ON q.queue_item_id=v.queue_item_id
  WHERE v.lease_active;
END
$function$;
