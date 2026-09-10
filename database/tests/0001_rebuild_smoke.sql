-- BT2 canonical blank-database smoke qualification.
-- Runs only after schema 0001/0002 and all executable migrations.
-- All fixture rows are rolled back.

BEGIN;

SELECT bt2.assert_internal_access_boundary_v1();

-- Minimal canonical topology fixture. The unit->orchestrator FK is deferred by design.
INSERT INTO bt2.agent_units(unit_key,display_name,unit_type,orchestrator_agent_key)
VALUES
  ('build_team','Build Team Two','ORCHESTRATED_TEAM','one'),
  ('independent','Independent','INDEPENDENT_AGENT',NULL);

INSERT INTO bt2.agents(agent_key,display_name,numerical_identity,unit_key,role_kind,role_summary)
VALUES
  ('one','One',1,'build_team','PRIMARY','CI primary'),
  ('two','Two',2,'build_team','SUBAGENT','CI subagent'),
  ('hephaestus','Hephaestus',NULL,'independent','INDEPENDENT','CI independent');

INSERT INTO bt2.agent_relationships(source_agent_key,target_agent_key,relation_type)
VALUES ('one','two','ORCHESTRATES');

DO $test$
BEGIN
  BEGIN
    INSERT INTO bt2.agent_relationships(source_agent_key,target_agent_key,relation_type)
    VALUES ('one','hephaestus','ORCHESTRATES');
    RAISE EXCEPTION 'EXPECTED_INVALID_ORCHESTRATION_REJECTION';
  EXCEPTION WHEN OTHERS THEN
    IF position('INVALID_ORCHESTRATION_EDGE' in SQLERRM)=0 THEN RAISE; END IF;
  END;
END
$test$;

-- Workspace checkpoint HEAD/CAS path.
INSERT INTO bt2.workspaces(workspace_key,owner_agent_key,status)
VALUES ('ci-workspace','two','ACTIVE');

WITH w AS (SELECT workspace_id FROM bt2.workspaces WHERE workspace_key='ci-workspace')
INSERT INTO bt2.workspace_checkpoints(
  workspace_id,predecessor_checkpoint_id,generation,payload,payload_digest_sha256,created_by_agent_key
)
SELECT workspace_id,NULL,1,'{"ci":true}'::jsonb,
       encode(public.digest(convert_to('{"ci":true}'::jsonb::text,'UTF8'),'sha256'),'hex'),'two'
FROM w;

DO $test$
BEGIN
  IF (SELECT generation FROM bt2.workspaces WHERE workspace_key='ci-workspace')<>1 THEN
    RAISE EXCEPTION 'WORKSPACE_HEAD_DID_NOT_ADVANCE';
  END IF;
END
$test$;

-- Queue V2 basic replay-safe path.
DO $test$
DECLARE v_item uuid; v_replay boolean; v_claim uuid:=gen_random_uuid(); v_token uuid; v_gen bigint; v_active boolean; v_ack boolean; v_ack_replay boolean;
BEGIN
  SELECT q.out_queue_item_id,q.idempotent_replay INTO STRICT v_item,v_replay
  FROM bt2.enqueue_work_v2('ci-dispatch-1','agent_dispatch','one','two','CI_WORK','{"ci":true}'::jsonb,10,NULL) q;
  IF v_replay THEN RAISE EXCEPTION 'FIRST_ENQUEUE_REPORTED_REPLAY'; END IF;

  PERFORM * FROM bt2.enqueue_work_v2('ci-dispatch-1','agent_dispatch','one','two','CI_WORK','{"ci":true}'::jsonb,10,NULL);
  IF (SELECT count(*) FROM bt2.work_queue WHERE enqueue_key='ci-dispatch-1')<>1 THEN
    RAISE EXCEPTION 'ENQUEUE_REPLAY_DUPLICATED';
  END IF;

  SELECT c.lease_token,c.claim_generation,c.lease_active INTO STRICT v_token,v_gen,v_active
  FROM bt2.claim_work_v2(v_claim,'agent_dispatch','two','ci-worker',120,1) c;
  IF v_gen<>1 OR NOT v_active THEN RAISE EXCEPTION 'CLAIM_INVALID'; END IF;

  SELECT a.acked,a.idempotent_replay INTO STRICT v_ack,v_ack_replay FROM bt2.ack_work_v2(v_item,v_token) a;
  IF NOT v_ack OR v_ack_replay THEN RAISE EXCEPTION 'FIRST_ACK_INVALID'; END IF;
  SELECT a.acked,a.idempotent_replay INTO STRICT v_ack,v_ack_replay FROM bt2.ack_work_v2(v_item,v_token) a;
  IF NOT v_ack OR NOT v_ack_replay THEN RAISE EXCEPTION 'ACK_REPLAY_INVALID'; END IF;
END
$test$;

-- BugOps basic report path + explicit severity normalization.
DO $test$
DECLARE v_bug uuid; v_event uuid; v_state bigint; v_route bigint; v_dispatch bigint; v_queue uuid; v_replay boolean;
BEGIN
  SELECT r.out_bug_id,r.out_event_id,r.out_state_version,r.out_routing_revision,
         r.out_dispatch_revision,r.out_queue_item_id,r.idempotent_replay
  INTO STRICT v_bug,v_event,v_state,v_route,v_dispatch,v_queue,v_replay
  FROM bt2.report_bug_v2(gen_random_uuid(),'ci-bug-1','CI bug','smoke','HIGH','ci','two','two','{}'::jsonb) r;
  IF v_state<>1 OR v_route<>1 OR v_dispatch<>1 OR v_replay THEN
    RAISE EXCEPTION 'BUG_REPORT_STATE_INVALID';
  END IF;
  IF (SELECT severity FROM bt2.bugs WHERE bug_id=v_bug)<>'SEV-1' THEN
    RAISE EXCEPTION 'BUG_SEVERITY_MAPPING_INVALID';
  END IF;
END
$test$;

-- No synthetic qualification fixture may be present after an empty rebuild.
DO $test$
BEGIN
  IF (SELECT count(*) FROM bt2.training_qualifications)<>0 THEN
    RAISE EXCEPTION 'QUALIFICATION_FABRICATED';
  END IF;
END
$test$;

ROLLBACK;
