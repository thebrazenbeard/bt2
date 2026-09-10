-- BT2 canonical BugOps convergence V1: behavior/API layer.
-- Applies after 0006 schema layer. Source owner: Two.

CREATE OR REPLACE FUNCTION bt2.record_bug_closure_evidence_v1(
  p_closure_evidence_id uuid,p_bug_id uuid,p_expected_state_version bigint,
  p_recorded_by_agent_key text,p_mechanism_bounded boolean,
  p_corrective_controls_resolved boolean,p_regression_cases_present boolean,
  p_review_path_complete_or_exception boolean,p_claimed_effect_verified boolean,
  p_unresolved_hypotheses_explicit boolean,p_evidence jsonb
) RETURNS uuid LANGUAGE plpgsql AS $function$
DECLARE v_digest text; v_existing record; v_bug record;
BEGIN
  IF p_closure_evidence_id IS NULL THEN RAISE EXCEPTION 'INVALID_CLOSURE_EVIDENCE_ID'; END IF;
  IF p_evidence IS NULL OR jsonb_typeof(p_evidence)<>'object' THEN RAISE EXCEPTION 'INVALID_CLOSURE_EVIDENCE'; END IF;
  IF p_recorded_by_agent_key IS NOT NULL AND NOT EXISTS(
    SELECT 1 FROM bt2.agents WHERE agent_key=p_recorded_by_agent_key AND active
  ) THEN RAISE EXCEPTION 'INVALID_ACTOR_AGENT'; END IF;
  v_digest:=encode(digest(convert_to(jsonb_build_object(
    'bug_id',p_bug_id,'state_version',p_expected_state_version,
    'recorded_by_agent_key',p_recorded_by_agent_key,
    'mechanism_bounded',p_mechanism_bounded,
    'corrective_controls_resolved',p_corrective_controls_resolved,
    'regression_cases_present',p_regression_cases_present,
    'review_path_complete_or_exception',p_review_path_complete_or_exception,
    'claimed_effect_verified',p_claimed_effect_verified,
    'unresolved_hypotheses_explicit',p_unresolved_hypotheses_explicit,
    'evidence',p_evidence
  )::text,'UTF8'),'sha256'),'hex');
  SELECT * INTO v_existing FROM bt2.bug_closure_evidence
  WHERE closure_evidence_id=p_closure_evidence_id;
  IF FOUND THEN
    IF v_existing.evidence_digest_sha256<>v_digest THEN
      RAISE EXCEPTION 'CLOSURE_EVIDENCE_ID_REUSE_CONFLICT';
    END IF;
    RETURN p_closure_evidence_id;
  END IF;
  SELECT * INTO v_bug FROM bt2.bugs WHERE bug_id=p_bug_id FOR SHARE;
  IF NOT FOUND THEN RAISE EXCEPTION 'BUG_NOT_FOUND'; END IF;
  IF v_bug.state_version<>p_expected_state_version THEN RAISE EXCEPTION 'STALE_STATE_VERSION'; END IF;
  INSERT INTO bt2.bug_closure_evidence(
    closure_evidence_id,bug_id,based_on_state_version,
    mechanism_bounded,corrective_controls_resolved,regression_cases_present,
    review_path_complete_or_exception,claimed_effect_verified,unresolved_hypotheses_explicit,
    evidence,evidence_digest_sha256,recorded_by_agent_key
  ) VALUES(
    p_closure_evidence_id,p_bug_id,p_expected_state_version,
    p_mechanism_bounded,p_corrective_controls_resolved,p_regression_cases_present,
    p_review_path_complete_or_exception,p_claimed_effect_verified,p_unresolved_hypotheses_explicit,
    p_evidence,v_digest,p_recorded_by_agent_key
  );
  RETURN p_closure_evidence_id;
END
$function$;

CREATE OR REPLACE FUNCTION bt2.report_bug_v2(
  p_operation_id uuid,p_intake_key text,p_title text,p_description text DEFAULT '',
  p_severity text DEFAULT 'SEV-2',p_component text DEFAULT NULL,p_reported_by text DEFAULT NULL,
  p_assigned_agent_key text DEFAULT 'one',p_evidence jsonb DEFAULT '{}'::jsonb
) RETURNS TABLE(
  out_bug_id uuid,out_event_id uuid,out_state_version bigint,out_routing_revision bigint,
  out_dispatch_revision bigint,out_queue_item_id uuid,idempotent_replay boolean
) LANGUAGE plpgsql AS $function$
DECLARE
  v_key text:=btrim(p_intake_key); v_title text:=btrim(p_title);
  v_severity text:=bt2.normalize_bug_severity_v1(p_severity);
  v_target text:=lower(btrim(p_assigned_agent_key)); v_actor text;
  v_request jsonb; v_intake_digest text; v_root uuid; v_attempt uuid; v_done uuid;
  v_op record; v_bug record; v_existing_event record;
  v_bug_id uuid:=gen_random_uuid(); v_event uuid:=gen_random_uuid(); v_queue uuid;
  v_q_replay boolean; v_snapshot jsonb; v_snapshot_digest text; v_result jsonb;
BEGIN
  IF v_key IS NULL OR v_key='' THEN RAISE EXCEPTION 'INVALID_INTAKE_KEY'; END IF;
  IF v_title IS NULL OR v_title='' THEN RAISE EXCEPTION 'INVALID_TITLE'; END IF;
  IF v_severity IS NULL THEN RAISE EXCEPTION 'INVALID_SEVERITY'; END IF;
  IF p_evidence IS NULL OR jsonb_typeof(p_evidence)<>'object' THEN RAISE EXCEPTION 'INVALID_EVIDENCE'; END IF;
  IF NOT EXISTS(SELECT 1 FROM bt2.agents WHERE agent_key=v_target AND active) THEN RAISE EXCEPTION 'INVALID_TARGET_AGENT'; END IF;
  SELECT agent_key INTO v_actor FROM bt2.agents
  WHERE agent_key=lower(coalesce(p_reported_by,'')) AND active;
  v_request:=jsonb_build_object(
    'kind','REPORT_BUG','intake_key',v_key,'title',v_title,
    'description',coalesce(p_description,''),'severity',v_severity,
    'component',p_component,'reported_by',p_reported_by,
    'assigned_agent_key',v_target,'evidence',p_evidence
  );
  v_intake_digest:=encode(digest(convert_to(v_request::text,'UTF8'),'sha256'),'hex');
  v_root:=bt2.prepare_operation_v1(
    p_operation_id,NULL,v_actor,NULL,'REPORT_BUG','bt2.bugs:intake:'||v_key,
    p_operation_id::text,v_request
  );
  SELECT * INTO v_op FROM bt2.operations WHERE operation_id=p_operation_id;
  IF v_op.state='VERIFIED' THEN
    RETURN QUERY SELECT
      (v_op.result_payload->>'bug_id')::uuid,(v_op.result_payload->>'event_id')::uuid,
      (v_op.result_payload->>'state_version')::bigint,
      (v_op.result_payload->>'routing_revision')::bigint,
      (v_op.result_payload->>'dispatch_revision')::bigint,
      (v_op.result_payload->>'queue_item_id')::uuid,true;
    RETURN;
  ELSIF v_op.state<>'PREPARED' THEN
    RAISE EXCEPTION USING MESSAGE='OPERATION_REQUIRES_RECONCILIATION state='||v_op.state;
  END IF;
  v_attempt:=bt2.append_operation_event_v1(
    p_operation_id,v_root,'ATTEMPTED',NULL,'inspect_before_retry'
  );
  SELECT * INTO v_bug FROM bt2.bugs WHERE intake_key=v_key FOR SHARE;
  IF FOUND THEN
    IF v_bug.intake_digest_sha256 IS DISTINCT FROM v_intake_digest THEN RAISE EXCEPTION 'INTAKE_KEY_REUSE_CONFLICT'; END IF;
    SELECT * INTO STRICT v_existing_event FROM bt2.bug_events
    WHERE bug_id=v_bug.bug_id AND state_version=1;
    v_result:=jsonb_build_object(
      'bug_id',v_bug.bug_id,'event_id',v_existing_event.bug_event_id,'state_version',1,
      'routing_revision',v_existing_event.routing_revision,
      'dispatch_revision',v_existing_event.dispatch_revision,
      'queue_item_id',v_existing_event.queue_item_id,'adopted_existing',true
    );
    v_done:=bt2.append_operation_event_v1(
      p_operation_id,v_attempt,'VERIFIED',NULL,'no_retry_required',
      'Existing intake adopted',v_result,
      jsonb_build_object('kind','BUG_REPORT_RECEIPT','bug_id',v_bug.bug_id,
                         'event_id',v_existing_event.bug_event_id)
    );
    RETURN QUERY SELECT v_bug.bug_id,v_existing_event.bug_event_id,1::bigint,
      v_existing_event.routing_revision,v_existing_event.dispatch_revision,
      v_existing_event.queue_item_id,true;
    RETURN;
  END IF;
  INSERT INTO bt2.bugs(
    bug_id,intake_key,intake_digest_sha256,title,description,severity,status,component,
    reported_by,assigned_agent_key,state_version,routing_revision,dispatch_revision,evidence
  ) VALUES(
    v_bug_id,v_key,v_intake_digest,v_title,coalesce(p_description,''),v_severity,'NEW',p_component,
    p_reported_by,v_target,1,1,1,p_evidence
  );
  v_snapshot:=jsonb_build_object(
    'bug_id',v_bug_id,'event_id',v_event,'state_version',1,'routing_revision',1,
    'dispatch_revision',1,'target_agent_key',v_target,'action','BUG_REPORTED',
    'operation_id',p_operation_id
  );
  v_snapshot_digest:=encode(digest(convert_to(v_snapshot::text,'UTF8'),'sha256'),'hex');
  SELECT out_queue_item_id,idempotent_replay INTO STRICT v_queue,v_q_replay
  FROM bt2.enqueue_work_v2(
    'bug:'||v_bug_id::text||':dispatch:1','agent_dispatch','one',v_target,
    'BUG_REPORTED',v_snapshot,10,NULL
  );
  INSERT INTO bt2.bug_events(
    bug_event_id,bug_id,state_version,routing_revision,dispatch_revision,event_type,
    actor_agent_key,operation_id,queue_item_id,request_digest_sha256,request_payload,
    details,dispatch_snapshot,dispatch_payload_digest_sha256
  ) VALUES(
    v_event,v_bug_id,1,1,1,'REPORTED',v_actor,p_operation_id,v_queue,
    v_op.request_digest_sha256,v_request,jsonb_build_object('assigned_agent_key',v_target),
    v_snapshot,v_snapshot_digest
  );
  v_result:=jsonb_build_object(
    'bug_id',v_bug_id,'event_id',v_event,'state_version',1,'routing_revision',1,
    'dispatch_revision',1,'queue_item_id',v_queue,'adopted_existing',false
  );
  v_done:=bt2.append_operation_event_v1(
    p_operation_id,v_attempt,'VERIFIED',NULL,'no_retry_required','Bug report committed',v_result,
    jsonb_build_object('kind','BUG_REPORT_RECEIPT','bug_id',v_bug_id,
                       'event_id',v_event,'queue_item_id',v_queue)
  );
  RETURN QUERY SELECT v_bug_id,v_event,1::bigint,1::bigint,1::bigint,v_queue,false;
END
$function$;

CREATE OR REPLACE FUNCTION bt2.report_bug(
  p_operation_id uuid,p_intake_key text,p_title text,p_description text DEFAULT '',
  p_severity text DEFAULT 'MEDIUM',p_component text DEFAULT NULL,p_reported_by text DEFAULT NULL,
  p_assigned_agent_key text DEFAULT 'one',p_evidence jsonb DEFAULT '{}'::jsonb
) RETURNS TABLE(out_bug_id uuid,out_event_id uuid,out_queue_item_id uuid,idempotent_replay boolean)
LANGUAGE sql AS $function$
  SELECT out_bug_id,out_event_id,out_queue_item_id,idempotent_replay
  FROM bt2.report_bug_v2(
    p_operation_id,p_intake_key,p_title,p_description,p_severity,p_component,
    p_reported_by,p_assigned_agent_key,p_evidence
  )
$function$;

CREATE OR REPLACE FUNCTION bt2.route_bug_v2(
  p_operation_id uuid,p_bug_id uuid,p_expected_state_version bigint,
  p_expected_dispatch_revision bigint,p_target_agent_key text,
  p_actor_agent_key text DEFAULT 'one',p_reason text DEFAULT NULL
) RETURNS TABLE(
  out_event_id uuid,out_state_version bigint,out_routing_revision bigint,
  out_dispatch_revision bigint,out_queue_item_id uuid,idempotent_replay boolean
) LANGUAGE plpgsql AS $function$
DECLARE
  v_target text:=lower(btrim(p_target_agent_key)); v_actor text:=lower(btrim(p_actor_agent_key));
  v_request jsonb; v_root uuid; v_attempt uuid; v_done uuid; v_op record; v_bug record;
  v_event uuid:=gen_random_uuid(); v_queue uuid; v_q_replay boolean;
  v_state bigint; v_route bigint; v_dispatch bigint;
  v_snapshot jsonb; v_snapshot_digest text; v_result jsonb;
BEGIN
  IF NOT EXISTS(SELECT 1 FROM bt2.agents WHERE agent_key=v_target AND active) THEN RAISE EXCEPTION 'INVALID_TARGET_AGENT'; END IF;
  IF NOT EXISTS(SELECT 1 FROM bt2.agents WHERE agent_key=v_actor AND active) THEN RAISE EXCEPTION 'INVALID_ACTOR_AGENT'; END IF;
  v_request:=jsonb_build_object(
    'kind','ROUTE_BUG','bug_id',p_bug_id,'expected_state_version',p_expected_state_version,
    'expected_dispatch_revision',p_expected_dispatch_revision,'target_agent_key',v_target,
    'actor_agent_key',v_actor,'reason',p_reason
  );
  v_root:=bt2.prepare_operation_v1(
    p_operation_id,NULL,v_actor,NULL,'ROUTE_BUG','bt2.bugs:'||p_bug_id::text,
    p_operation_id::text,v_request
  );
  SELECT * INTO v_op FROM bt2.operations WHERE operation_id=p_operation_id;
  IF v_op.state='VERIFIED' THEN
    RETURN QUERY SELECT
      (v_op.result_payload->>'event_id')::uuid,
      (v_op.result_payload->>'state_version')::bigint,
      (v_op.result_payload->>'routing_revision')::bigint,
      (v_op.result_payload->>'dispatch_revision')::bigint,
      (v_op.result_payload->>'queue_item_id')::uuid,true;
    RETURN;
  ELSIF v_op.state<>'PREPARED' THEN
    RAISE EXCEPTION USING MESSAGE='OPERATION_REQUIRES_RECONCILIATION state='||v_op.state;
  END IF;
  SELECT * INTO v_bug FROM bt2.bugs WHERE bug_id=p_bug_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'BUG_NOT_FOUND'; END IF;
  IF v_bug.state_version<>p_expected_state_version THEN RAISE EXCEPTION 'STALE_STATE_VERSION'; END IF;
  IF v_bug.dispatch_revision<>p_expected_dispatch_revision THEN RAISE EXCEPTION 'STALE_DISPATCH_REVISION'; END IF;
  IF v_bug.status='CLOSED' THEN RAISE EXCEPTION 'BUG_CLOSED'; END IF;
  v_attempt:=bt2.append_operation_event_v1(
    p_operation_id,v_root,'ATTEMPTED',NULL,'inspect_before_retry'
  );
  v_state:=v_bug.state_version+1;
  v_route:=v_bug.routing_revision+1;
  v_dispatch:=v_bug.dispatch_revision+1;
  v_snapshot:=jsonb_build_object(
    'bug_id',p_bug_id,'event_id',v_event,'state_version',v_state,
    'routing_revision',v_route,'dispatch_revision',v_dispatch,
    'target_agent_key',v_target,'action','BUG_ROUTED','operation_id',p_operation_id
  );
  v_snapshot_digest:=encode(digest(convert_to(v_snapshot::text,'UTF8'),'sha256'),'hex');
  SELECT out_queue_item_id,idempotent_replay INTO STRICT v_queue,v_q_replay
  FROM bt2.enqueue_work_v2(
    'bug:'||p_bug_id::text||':dispatch:'||v_dispatch::text,
    'agent_dispatch',v_actor,v_target,'BUG_ROUTED',v_snapshot,10,NULL
  );
  UPDATE bt2.bugs SET assigned_agent_key=v_target,state_version=v_state,
    routing_revision=v_route,dispatch_revision=v_dispatch,updated_at=clock_timestamp()
  WHERE bug_id=p_bug_id;
  INSERT INTO bt2.bug_events(
    bug_event_id,bug_id,state_version,routing_revision,dispatch_revision,event_type,
    actor_agent_key,operation_id,queue_item_id,request_digest_sha256,request_payload,
    details,dispatch_snapshot,dispatch_payload_digest_sha256
  ) VALUES(
    v_event,p_bug_id,v_state,v_route,v_dispatch,'ROUTED',v_actor,p_operation_id,v_queue,
    v_op.request_digest_sha256,v_request,
    jsonb_build_object('from_agent_key',v_bug.assigned_agent_key,
                       'to_agent_key',v_target,'reason',p_reason),
    v_snapshot,v_snapshot_digest
  );
  v_result:=jsonb_build_object(
    'event_id',v_event,'state_version',v_state,'routing_revision',v_route,
    'dispatch_revision',v_dispatch,'queue_item_id',v_queue
  );
  v_done:=bt2.append_operation_event_v1(
    p_operation_id,v_attempt,'VERIFIED',NULL,'no_retry_required','Bug route committed',v_result,
    jsonb_build_object('kind','BUG_ROUTE_RECEIPT','bug_id',p_bug_id,
                       'event_id',v_event,'queue_item_id',v_queue)
  );
  RETURN QUERY SELECT v_event,v_state,v_route,v_dispatch,v_queue,false;
END
$function$;

CREATE OR REPLACE FUNCTION bt2.route_bug(
  p_operation_id uuid,p_bug_id uuid,p_expected_state_version bigint,
  p_target_agent_key text,p_actor_agent_key text DEFAULT 'one',p_reason text DEFAULT NULL
) RETURNS TABLE(out_event_id uuid,out_state_version bigint,out_queue_item_id uuid,idempotent_replay boolean)
LANGUAGE plpgsql AS $function$
DECLARE v_dispatch bigint;
BEGIN
  SELECT dispatch_revision INTO STRICT v_dispatch FROM bt2.bugs WHERE bug_id=p_bug_id;
  RETURN QUERY SELECT r.out_event_id,r.out_state_version,r.out_queue_item_id,r.idempotent_replay
  FROM bt2.route_bug_v2(
    p_operation_id,p_bug_id,p_expected_state_version,v_dispatch,
    p_target_agent_key,p_actor_agent_key,p_reason
  ) r;
END
$function$;

CREATE OR REPLACE FUNCTION bt2.update_bug_status_v2(
  p_operation_id uuid,p_bug_id uuid,p_expected_state_version bigint,p_status text,
  p_actor_agent_key text DEFAULT 'one',p_note text DEFAULT NULL
) RETURNS TABLE(
  out_event_id uuid,out_state_version bigint,out_status text,out_routing_revision bigint,
  out_dispatch_revision bigint,out_queue_item_id uuid,idempotent_replay boolean
) LANGUAGE plpgsql AS $function$
DECLARE
  v_requested text:=upper(btrim(p_status)); v_actor text:=lower(btrim(p_actor_agent_key));
  v_request jsonb; v_root uuid; v_attempt uuid; v_done uuid; v_op record; v_bug record; v_close record;
  v_event uuid:=gen_random_uuid(); v_state bigint; v_status text;
  v_route bigint; v_dispatch bigint; v_target text; v_queue uuid;
  v_q_replay boolean; v_snapshot jsonb; v_snapshot_digest text; v_result jsonb;
BEGIN
  IF v_requested NOT IN ('NEW','TRIAGED','IN_PROGRESS','BLOCKED','FIXED','VERIFYING','CLOSED','REOPENED') THEN
    RAISE EXCEPTION 'INVALID_STATUS';
  END IF;
  IF NOT EXISTS(SELECT 1 FROM bt2.agents WHERE agent_key=v_actor AND active) THEN RAISE EXCEPTION 'INVALID_ACTOR_AGENT'; END IF;
  v_request:=jsonb_build_object(
    'kind','UPDATE_BUG_STATUS','bug_id',p_bug_id,
    'expected_state_version',p_expected_state_version,'requested_status',v_requested,
    'actor_agent_key',v_actor,'note',p_note
  );
  v_root:=bt2.prepare_operation_v1(
    p_operation_id,NULL,v_actor,NULL,'UPDATE_BUG_STATUS','bt2.bugs:'||p_bug_id::text,
    p_operation_id::text,v_request
  );
  SELECT * INTO v_op FROM bt2.operations WHERE operation_id=p_operation_id;
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
  SELECT * INTO v_bug FROM bt2.bugs WHERE bug_id=p_bug_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'BUG_NOT_FOUND'; END IF;
  IF v_bug.state_version<>p_expected_state_version THEN RAISE EXCEPTION 'STALE_STATE_VERSION'; END IF;
  IF v_requested='REOPENED' AND v_bug.status<>'CLOSED' THEN RAISE EXCEPTION 'REOPEN_REQUIRES_CLOSED'; END IF;
  IF v_bug.status='CLOSED' AND v_requested<>'REOPENED' THEN RAISE EXCEPTION 'BUG_CLOSED_REQUIRES_REOPEN'; END IF;
  IF v_requested='CLOSED' THEN
    SELECT * INTO v_close FROM bt2.bug_closure_evidence
    WHERE bug_id=p_bug_id AND based_on_state_version=v_bug.state_version
      AND mechanism_bounded AND corrective_controls_resolved AND regression_cases_present
      AND review_path_complete_or_exception AND claimed_effect_verified
      AND unresolved_hypotheses_explicit
    ORDER BY created_at DESC,closure_evidence_id DESC LIMIT 1;
    IF NOT FOUND THEN RAISE EXCEPTION 'CLOSURE_EVIDENCE_INCOMPLETE_OR_STALE'; END IF;
  END IF;
  v_attempt:=bt2.append_operation_event_v1(
    p_operation_id,v_root,'ATTEMPTED',NULL,'inspect_before_retry'
  );
  v_state:=v_bug.state_version+1;
  v_route:=v_bug.routing_revision;
  v_dispatch:=v_bug.dispatch_revision;
  v_queue:=NULL;
  IF v_requested='REOPENED' THEN
    v_status:='NEW'; v_target:='one'; v_dispatch:=v_bug.dispatch_revision+1;
    IF v_bug.assigned_agent_key IS DISTINCT FROM v_target THEN v_route:=v_bug.routing_revision+1; END IF;
    v_snapshot:=jsonb_build_object(
      'bug_id',p_bug_id,'event_id',v_event,'state_version',v_state,
      'routing_revision',v_route,'dispatch_revision',v_dispatch,
      'target_agent_key',v_target,'action','BUG_REOPENED','operation_id',p_operation_id
    );
    v_snapshot_digest:=encode(digest(convert_to(v_snapshot::text,'UTF8'),'sha256'),'hex');
    SELECT out_queue_item_id,idempotent_replay INTO STRICT v_queue,v_q_replay
    FROM bt2.enqueue_work_v2(
      'bug:'||p_bug_id::text||':dispatch:'||v_dispatch::text,
      'agent_dispatch',v_actor,v_target,'BUG_REOPENED',v_snapshot,10,NULL
    );
    UPDATE bt2.bugs SET status='NEW',assigned_agent_key=v_target,state_version=v_state,
      routing_revision=v_route,dispatch_revision=v_dispatch,
      updated_at=clock_timestamp(),closed_at=NULL WHERE bug_id=p_bug_id;
  ELSE
    v_status:=v_requested;
    IF v_status='CLOSED' THEN v_dispatch:=v_bug.dispatch_revision+1; END IF;
    UPDATE bt2.bugs SET status=v_status,state_version=v_state,dispatch_revision=v_dispatch,
      updated_at=clock_timestamp(),
      closed_at=CASE WHEN v_status='CLOSED' THEN clock_timestamp() ELSE closed_at END
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
    jsonb_build_object(
      'from_status',v_bug.status,'to_status',v_status,'note',p_note,
      'closure_evidence_id',CASE WHEN v_requested='CLOSED' THEN v_close.closure_evidence_id ELSE NULL END
    ),v_snapshot,v_snapshot_digest
  );
  v_result:=jsonb_build_object(
    'event_id',v_event,'state_version',v_state,'status',v_status,
    'routing_revision',v_route,'dispatch_revision',v_dispatch,'queue_item_id',v_queue
  );
  v_done:=bt2.append_operation_event_v1(
    p_operation_id,v_attempt,'VERIFIED',NULL,'no_retry_required','Bug status committed',v_result,
    jsonb_build_object('kind','BUG_STATUS_RECEIPT','bug_id',p_bug_id,'event_id',v_event)
  );
  RETURN QUERY SELECT v_event,v_state,v_status,v_route,v_dispatch,v_queue,false;
END
$function$;

CREATE OR REPLACE FUNCTION bt2.update_bug_status(
  p_operation_id uuid,p_bug_id uuid,p_expected_state_version bigint,p_status text,
  p_actor_agent_key text DEFAULT 'one',p_note text DEFAULT NULL
) RETURNS TABLE(out_event_id uuid,out_state_version bigint,out_status text,out_queue_item_id uuid,idempotent_replay boolean)
LANGUAGE sql AS $function$
  SELECT out_event_id,out_state_version,out_status,out_queue_item_id,idempotent_replay
  FROM bt2.update_bug_status_v2(
    p_operation_id,p_bug_id,p_expected_state_version,p_status,p_actor_agent_key,p_note
  )
$function$;

CREATE OR REPLACE FUNCTION bt2.validate_bug_dispatch_v1(
  p_queue_item_id uuid,p_lease_token uuid
) RETURNS boolean LANGUAGE plpgsql AS $function$
DECLARE q record; b record; v_bug uuid; v_dispatch bigint;
BEGIN
  SELECT * INTO q FROM bt2.work_queue WHERE queue_item_id=p_queue_item_id;
  IF NOT FOUND OR q.state<>'CLAIMED' OR q.lease_token IS DISTINCT FROM p_lease_token
     OR q.lease_until<clock_timestamp() THEN RAISE EXCEPTION 'STALE_OR_INVALID_LEASE'; END IF;
  IF q.work_kind NOT IN ('BUG_REPORTED','BUG_ROUTED','BUG_REOPENED') THEN RAISE EXCEPTION 'NOT_BUG_DISPATCH'; END IF;
  v_bug:=nullif(q.payload->>'bug_id','')::uuid;
  v_dispatch:=nullif(q.payload->>'dispatch_revision','')::bigint;
  SELECT * INTO b FROM bt2.bugs WHERE bug_id=v_bug;
  IF NOT FOUND THEN RAISE EXCEPTION 'BUG_NOT_FOUND'; END IF;
  IF b.status='CLOSED' OR b.dispatch_revision<>v_dispatch
     OR b.assigned_agent_key IS DISTINCT FROM q.target_agent_key THEN
    RAISE EXCEPTION 'STALE_BUG_DISPATCH';
  END IF;
  RETURN true;
END
$function$;
