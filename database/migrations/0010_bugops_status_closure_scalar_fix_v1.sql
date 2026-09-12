-- BugOps runtime qualification correction V3.
-- Avoids dereferencing an unassigned record on non-CLOSED status transitions.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.

CREATE OR REPLACE FUNCTION bt2.update_bug_status_v2(
  p_operation_id uuid,p_bug_id uuid,p_expected_state_version bigint,p_status text,
  p_actor_agent_key text DEFAULT 'one',p_note text DEFAULT NULL
) RETURNS TABLE(
  out_event_id uuid,out_state_version bigint,out_status text,out_routing_revision bigint,
  out_dispatch_revision bigint,out_queue_item_id uuid,idempotent_replay boolean
) LANGUAGE plpgsql AS $function$
DECLARE
  v_requested text:=upper(btrim(p_status)); v_actor text:=lower(btrim(p_actor_agent_key));
  v_request jsonb; v_root uuid; v_attempt uuid; v_done uuid; v_op record; v_bug record;
  v_close_id uuid:=NULL;
  v_event uuid:=gen_random_uuid(); v_state bigint; v_status text; v_route bigint; v_dispatch bigint;
  v_target text; v_queue uuid; v_q_replay boolean; v_snapshot jsonb; v_snapshot_digest text; v_result jsonb;
BEGIN
  IF v_requested NOT IN ('NEW','TRIAGED','IN_PROGRESS','BLOCKED','FIXED','VERIFYING','CLOSED','REOPENED') THEN RAISE EXCEPTION 'INVALID_STATUS'; END IF;
  IF NOT EXISTS(SELECT 1 FROM bt2.agents WHERE agent_key=v_actor AND active) THEN RAISE EXCEPTION 'INVALID_ACTOR_AGENT'; END IF;
  v_request:=jsonb_build_object('kind','UPDATE_BUG_STATUS','bug_id',p_bug_id,
    'expected_state_version',p_expected_state_version,'requested_status',v_requested,
    'actor_agent_key',v_actor,'note',p_note);
  v_root:=bt2.prepare_operation_v1(p_operation_id,NULL,v_actor,NULL,'UPDATE_BUG_STATUS',
    'bt2.bugs:'||p_bug_id::text,p_operation_id::text,v_request);
  SELECT o.* INTO v_op FROM bt2.operations o WHERE o.operation_id=p_operation_id;
  IF v_op.state='VERIFIED' THEN
    RETURN QUERY SELECT
      (v_op.result_payload->>'event_id')::uuid,
      (v_op.result_payload->>'state_version')::bigint,
      v_op.result_payload->>'status',
      (v_op.result_payload->>'routing_revision')::bigint,
      (v_op.result_payload->>'dispatch_revision')::bigint,
      nullif(v_op.result_payload->>'queue_item_id','')::uuid,true;
    RETURN;
  ELSIF v_op.state<>'PREPARED' THEN
    RAISE EXCEPTION USING MESSAGE='OPERATION_REQUIRES_RECONCILIATION state='||v_op.state;
  END IF;
  SELECT b.* INTO v_bug FROM bt2.bugs b WHERE b.bug_id=p_bug_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'BUG_NOT_FOUND'; END IF;
  IF v_bug.state_version<>p_expected_state_version THEN RAISE EXCEPTION 'STALE_STATE_VERSION'; END IF;
  IF v_requested='REOPENED' AND v_bug.status<>'CLOSED' THEN RAISE EXCEPTION 'REOPEN_REQUIRES_CLOSED'; END IF;
  IF v_bug.status='CLOSED' AND v_requested<>'REOPENED' THEN RAISE EXCEPTION 'BUG_CLOSED_REQUIRES_REOPEN'; END IF;
  IF v_requested='CLOSED' THEN
    SELECT c.closure_evidence_id INTO v_close_id FROM bt2.bug_closure_evidence c
    WHERE c.bug_id=p_bug_id AND c.based_on_state_version=v_bug.state_version
      AND c.mechanism_bounded AND c.corrective_controls_resolved AND c.regression_cases_present
      AND c.review_path_complete_or_exception AND c.claimed_effect_verified
      AND c.unresolved_hypotheses_explicit
    ORDER BY c.created_at DESC,c.closure_evidence_id DESC LIMIT 1;
    IF v_close_id IS NULL THEN RAISE EXCEPTION 'CLOSURE_EVIDENCE_INCOMPLETE_OR_STALE'; END IF;
  END IF;
  v_attempt:=bt2.append_operation_event_v1(p_operation_id,v_root,'ATTEMPTED',NULL,'inspect_before_retry');
  v_state:=v_bug.state_version+1;
  v_route:=v_bug.routing_revision;
  v_dispatch:=v_bug.dispatch_revision;
  v_queue:=NULL;
  IF v_requested='REOPENED' THEN
    v_status:='NEW'; v_target:='one'; v_dispatch:=v_bug.dispatch_revision+1;
    IF v_bug.assigned_agent_key IS DISTINCT FROM v_target THEN v_route:=v_bug.routing_revision+1; END IF;
    v_snapshot:=jsonb_build_object('bug_id',p_bug_id,'event_id',v_event,'state_version',v_state,
      'routing_revision',v_route,'dispatch_revision',v_dispatch,'target_agent_key',v_target,
      'action','BUG_REOPENED','operation_id',p_operation_id);
    v_snapshot_digest:=encode(digest(convert_to(v_snapshot::text,'UTF8'),'sha256'),'hex');
    SELECT q.out_queue_item_id,q.idempotent_replay INTO STRICT v_queue,v_q_replay
    FROM bt2.enqueue_work_v2('bug:'||p_bug_id::text||':dispatch:'||v_dispatch::text,
      'agent_dispatch',v_actor,v_target,'BUG_REOPENED',v_snapshot,10,NULL) AS q;
    UPDATE bt2.bugs SET status='NEW',assigned_agent_key=v_target,state_version=v_state,
      routing_revision=v_route,dispatch_revision=v_dispatch,updated_at=clock_timestamp(),closed_at=NULL
    WHERE bug_id=p_bug_id;
  ELSE
    v_status:=v_requested;
    IF v_status='CLOSED' THEN v_dispatch:=v_bug.dispatch_revision+1; END IF;
    UPDATE bt2.bugs SET status=v_status,state_version=v_state,dispatch_revision=v_dispatch,
      updated_at=clock_timestamp(),closed_at=CASE WHEN v_status='CLOSED' THEN clock_timestamp() ELSE closed_at END
    WHERE bug_id=p_bug_id;
  END IF;
  INSERT INTO bt2.bug_events(
    bug_event_id,bug_id,state_version,routing_revision,dispatch_revision,event_type,
    actor_agent_key,operation_id,queue_item_id,request_digest_sha256,request_payload,
    details,dispatch_snapshot,dispatch_payload_digest_sha256
  ) VALUES(
    v_event,p_bug_id,v_state,v_route,v_dispatch,
    CASE WHEN v_requested='REOPENED' THEN 'REOPENED' ELSE 'STATUS_CHANGED' END,
    v_actor,p_operation_id,v_queue,v_op.request_digest_sha256,v_request,
    jsonb_build_object('from_status',v_bug.status,'to_status',v_status,'note',p_note,
      'closure_evidence_id',v_close_id),
    v_snapshot,v_snapshot_digest
  );
  v_result:=jsonb_build_object('event_id',v_event,'state_version',v_state,'status',v_status,
    'routing_revision',v_route,'dispatch_revision',v_dispatch,'queue_item_id',v_queue);
  v_done:=bt2.append_operation_event_v1(p_operation_id,v_attempt,'VERIFIED',NULL,'no_retry_required',
    'Bug status committed',v_result,jsonb_build_object('kind','BUG_STATUS_RECEIPT','bug_id',p_bug_id,'event_id',v_event));
  RETURN QUERY SELECT v_event,v_state,v_status,v_route,v_dispatch,v_queue,false;
END
$function$;
