-- BugOps runtime qualification correction V1.
-- The enclosing RETURNS TABLE names overlap enqueue_work_v2 output names in PL/pgSQL.
-- Qualify the nested result columns explicitly; semantics are otherwise unchanged from 0007.

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
  SELECT a.agent_key INTO v_actor FROM bt2.agents a
  WHERE a.agent_key=lower(coalesce(p_reported_by,'')) AND a.active;
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
  SELECT o.* INTO v_op FROM bt2.operations o WHERE o.operation_id=p_operation_id;
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
  SELECT b.* INTO v_bug FROM bt2.bugs b WHERE b.intake_key=v_key FOR SHARE;
  IF FOUND THEN
    IF v_bug.intake_digest_sha256 IS DISTINCT FROM v_intake_digest THEN RAISE EXCEPTION 'INTAKE_KEY_REUSE_CONFLICT'; END IF;
    SELECT e.* INTO STRICT v_existing_event FROM bt2.bug_events e
    WHERE e.bug_id=v_bug.bug_id AND e.state_version=1;
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
  SELECT e.out_queue_item_id,e.idempotent_replay INTO STRICT v_queue,v_q_replay
  FROM bt2.enqueue_work_v2(
    'bug:'||v_bug_id::text||':dispatch:1','agent_dispatch','one',v_target,
    'BUG_REPORTED',v_snapshot,10,NULL
  ) AS e;
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
