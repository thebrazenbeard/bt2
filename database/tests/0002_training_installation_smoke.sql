-- BT2 training qualification/installation blank-rebuild smoke.
-- Synthetic fixtures only; entire test rolls back.

BEGIN;

INSERT INTO bt2.agent_units(unit_key,display_name,unit_type,orchestrator_agent_key)
VALUES ('build_team_install_test','BT2 install test','ORCHESTRATED_TEAM','one');

INSERT INTO bt2.agents(agent_key,display_name,numerical_identity,unit_key,role_kind,role_summary)
VALUES
  ('one','One',1,'build_team_install_test','PRIMARY','CI primary'),
  ('two','Two',2,'build_team_install_test','SUBAGENT','CI subagent'),
  ('three','Three',3,'build_team_install_test','SUBAGENT','CI subagent');

INSERT INTO bt2.agent_relationships(source_agent_key,target_agent_key,relation_type)
VALUES ('one','two','ORCHESTRATES'),('one','three','ORCHESTRATES');

DO $test$
DECLARE
  v_pkg uuid:=gen_random_uuid();
  v_q1 uuid:=gen_random_uuid();
  v_q2 uuid:=gen_random_uuid();
  v_q3 uuid:=gen_random_uuid();
  v_binding1 uuid;
  v_event1 uuid;
  v_binding2 uuid;
  v_event2 uuid;
  v_binding3 uuid;
  v_event3 uuid;
  v_stage_binding uuid;
  v_stage_event uuid;
  v_three_runtime uuid:=gen_random_uuid();
  v_rejected boolean;
  v_effective text;
  v_valid boolean;
BEGIN
  INSERT INTO bt2.training_packages(
    training_package_id,agent_key,version,status,source_binding_state,compatibility_state,metadata
  ) VALUES(v_pkg,'two','ci-install-v1','REGISTERED','DISCOVERED','UNASSESSED','{}'::jsonb);

  INSERT INTO bt2.training_qualifications(
    qualification_id,agent_key,training_package_id,outcome,evaluator,evidence
  ) VALUES(v_q1,'two',v_pkg,'PASS','ci','{"probe":true}'::jsonb);

  UPDATE bt2.training_packages
  SET compatibility_state='COMPATIBLE',status='QUALIFIED_BASE'
  WHERE training_package_id=v_pkg;

  SELECT x.out_binding_id,x.out_event_id
  INTO STRICT v_binding1,v_event1
  FROM bt2.begin_training_installation_evidence_v1(
    'two',v_pkg,v_q1,'CHATGPT_PROJECT','chatgpt://ci-one',NULL,'ACTIVE','{"observed":true}'::jsonb
  ) x;

  SELECT effective_state,activation_currently_valid
  INTO STRICT v_effective,v_valid
  FROM bt2.training_installation_effective_v1
  WHERE binding_id=v_binding1;
  IF v_effective<>'ACTIVE' OR NOT v_valid THEN
    RAISE EXCEPTION 'VALID_ACTIVE_NOT_EFFECTIVE';
  END IF;

  v_rejected:=false;
  BEGIN
    PERFORM * FROM bt2.begin_training_installation_evidence_v1(
      'two',v_pkg,v_q1,'CHATGPT_PROJECT','chatgpt://ci-two',NULL,'ACTIVE','{"observed":true}'::jsonb
    );
  EXCEPTION WHEN OTHERS THEN
    IF position('AGENT_ALREADY_HAS_ACTIVE_TRAINING_BINDING' in SQLERRM)>0 THEN v_rejected:=true; ELSE RAISE; END IF;
  END;
  IF NOT v_rejected THEN RAISE EXCEPTION 'SECOND_CURRENT_ACTIVE_ACCEPTED'; END IF;

  v_rejected:=false;
  BEGIN
    UPDATE bt2.training_installation_events
    SET evidence='{"tampered":true}'::jsonb
    WHERE installation_event_id=v_event1;
  EXCEPTION WHEN OTHERS THEN
    IF position('TRAINING_INSTALLATION_HISTORY_IS_APPEND_ONLY' in SQLERRM)>0 THEN v_rejected:=true; ELSE RAISE; END IF;
  END;
  IF NOT v_rejected THEN RAISE EXCEPTION 'INSTALLATION_HISTORY_MUTATED'; END IF;

  v_rejected:=false;
  BEGIN
    UPDATE bt2.training_qualifications SET outcome='RETRACTED' WHERE qualification_id=v_q1;
  EXCEPTION WHEN OTHERS THEN
    IF position('TRAINING_QUALIFICATION_HISTORY_IS_APPEND_ONLY' in SQLERRM)>0 THEN v_rejected:=true; ELSE RAISE; END IF;
  END;
  IF NOT v_rejected THEN RAISE EXCEPTION 'QUALIFICATION_HISTORY_MUTATED'; END IF;

  INSERT INTO bt2.runtime_sessions(runtime_session_id,agent_key,runtime_kind,status,metadata)
  VALUES(v_three_runtime,'three','CI','ACTIVE','{}'::jsonb);
  v_rejected:=false;
  BEGIN
    PERFORM * FROM bt2.begin_training_installation_evidence_v1(
      'two',v_pkg,NULL,'RUNTIME_SESSION',NULL,v_three_runtime,'INSTALLED','{"observed":true}'::jsonb
    );
  EXCEPTION WHEN foreign_key_violation THEN
    v_rejected:=true;
  END;
  IF NOT v_rejected THEN RAISE EXCEPTION 'CROSS_AGENT_RUNTIME_INSTALLATION_ACCEPTED'; END IF;

  SELECT x.out_binding_id,x.out_event_id
  INTO STRICT v_stage_binding,v_stage_event
  FROM bt2.begin_training_installation_evidence_v1(
    'two',v_pkg,NULL,'CHATGPT_PROJECT','chatgpt://ci-stage',NULL,'STAGED','{"observed":true}'::jsonb
  ) x;
  v_rejected:=false;
  BEGIN
    PERFORM bt2.append_training_installation_evidence_v1(
      v_stage_event,v_q1,'ACTIVE','{"observed":true}'::jsonb
    );
  EXCEPTION WHEN OTHERS THEN
    IF position('TRAINING_INSTALLATION_TRANSITION_INVALID' in SQLERRM)>0 THEN v_rejected:=true; ELSE RAISE; END IF;
  END;
  IF NOT v_rejected THEN RAISE EXCEPTION 'INVALID_STAGED_TO_ACTIVE_ACCEPTED'; END IF;

  PERFORM bt2.append_training_installation_evidence_v1(
    v_event1,v_q1,'INACTIVE','{"observed":true}'::jsonb
  );

  SELECT x.out_binding_id,x.out_event_id
  INTO STRICT v_binding2,v_event2
  FROM bt2.begin_training_installation_evidence_v1(
    'two',v_pkg,v_q1,'CHATGPT_PROJECT','chatgpt://ci-two',NULL,'ACTIVE','{"observed":true}'::jsonb
  ) x;

  INSERT INTO bt2.training_qualifications(
    qualification_id,agent_key,training_package_id,outcome,evaluator,evidence,qualified_at
  ) VALUES(v_q2,'two',v_pkg,'RETRACTED','ci','{"reason":"ci"}'::jsonb,clock_timestamp()+interval '1 microsecond');

  SELECT effective_state,activation_currently_valid
  INTO STRICT v_effective,v_valid
  FROM bt2.training_installation_effective_v1
  WHERE binding_id=v_binding2;
  IF v_effective<>'INVALIDATED' OR v_valid IS DISTINCT FROM false THEN
    RAISE EXCEPTION 'RETRACTED_QUALIFICATION_DID_NOT_INVALIDATE_ACTIVE';
  END IF;

  v_rejected:=false;
  BEGIN
    PERFORM * FROM bt2.begin_training_installation_evidence_v1(
      'two',v_pkg,v_q1,'CHATGPT_PROJECT','chatgpt://ci-three',NULL,'ACTIVE','{"observed":true}'::jsonb
    );
  EXCEPTION WHEN OTHERS THEN
    IF position('ACTIVE_TRAINING_REQUIRES_CURRENT_PASS_QUALIFICATION' in SQLERRM)>0 THEN v_rejected:=true; ELSE RAISE; END IF;
  END;
  IF NOT v_rejected THEN RAISE EXCEPTION 'STALE_PASS_ACTIVATION_ACCEPTED'; END IF;

  INSERT INTO bt2.training_qualifications(
    qualification_id,agent_key,training_package_id,outcome,evaluator,evidence,qualified_at
  ) VALUES(v_q3,'two',v_pkg,'PASS','ci','{"fresh":true}'::jsonb,clock_timestamp()+interval '2 microseconds');

  SELECT x.out_binding_id,x.out_event_id
  INTO STRICT v_binding3,v_event3
  FROM bt2.begin_training_installation_evidence_v1(
    'two',v_pkg,v_q3,'CHATGPT_PROJECT','chatgpt://ci-three',NULL,'ACTIVE','{"observed":true}'::jsonb
  ) x;

  SELECT effective_state,activation_currently_valid
  INTO STRICT v_effective,v_valid
  FROM bt2.training_installation_effective_v1
  WHERE binding_id=v_binding3;
  IF v_effective<>'ACTIVE' OR NOT v_valid THEN
    RAISE EXCEPTION 'FRESH_PASS_DID_NOT_REACTIVATE';
  END IF;
END
$test$;

ROLLBACK;
