-- BT2 canonical integrity hardening V1: identity, topology, training continuity,
-- checkpoint lineage, and append-only external-effect history.
-- Apply only after database/schema/0001 and 0002.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.

-- 1. Runtime/session provenance is not durable agent identity.
CREATE TABLE bt2.runtime_sessions (
  runtime_session_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_key text NOT NULL REFERENCES bt2.agents(agent_key),
  runtime_kind text NOT NULL,
  runtime_locator text,
  transport_locator text,
  status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','CLOSED','LOST','SUPERSEDED')),
  started_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  ended_at timestamptz,
  restored_from_checkpoint_id uuid REFERENCES bt2.operational_checkpoints(checkpoint_id),
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  CHECK ((status='ACTIVE' AND ended_at IS NULL) OR status<>'ACTIVE')
);
CREATE UNIQUE INDEX runtime_sessions_one_active_locator_v1
  ON bt2.runtime_sessions(runtime_locator)
  WHERE status='ACTIVE' AND runtime_locator IS NOT NULL;

-- 2. Topology shape is enforced, not merely represented by current rows.
ALTER TABLE bt2.agent_units
  ADD CONSTRAINT agent_units_orchestrator_agent_key_fkey
  FOREIGN KEY (orchestrator_agent_key) REFERENCES bt2.agents(agent_key)
  DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE bt2.agent_units
  ADD CONSTRAINT agent_units_orchestrator_shape_check
  CHECK ((unit_type='ORCHESTRATED_TEAM' AND orchestrator_agent_key IS NOT NULL)
      OR (unit_type<>'ORCHESTRATED_TEAM' AND orchestrator_agent_key IS NULL));

CREATE OR REPLACE FUNCTION bt2.validate_agent_unit_role_v1()
RETURNS trigger LANGUAGE plpgsql AS $function$
DECLARE v_unit record;
BEGIN
  SELECT * INTO STRICT v_unit FROM bt2.agent_units WHERE unit_key=NEW.unit_key;
  IF v_unit.unit_type='ORCHESTRATED_TEAM' THEN
    IF NEW.role_kind NOT IN ('PRIMARY','SUBAGENT') THEN RAISE EXCEPTION 'ROLE_UNIT_MISMATCH'; END IF;
    IF NEW.role_kind='PRIMARY' AND NEW.agent_key<>v_unit.orchestrator_agent_key THEN RAISE EXCEPTION 'PRIMARY_NOT_UNIT_ORCHESTRATOR'; END IF;
    IF NEW.role_kind='SUBAGENT' AND NEW.agent_key=v_unit.orchestrator_agent_key THEN RAISE EXCEPTION 'ORCHESTRATOR_CANNOT_BE_SUBAGENT'; END IF;
  ELSIF v_unit.unit_type='PAIRED_TEAM' THEN
    IF NEW.role_kind<>'PAIRED' THEN RAISE EXCEPTION 'ROLE_UNIT_MISMATCH'; END IF;
  ELSIF v_unit.unit_type='INDEPENDENT_AGENT' THEN
    IF NEW.role_kind<>'INDEPENDENT' THEN RAISE EXCEPTION 'ROLE_UNIT_MISMATCH'; END IF;
  ELSE
    RAISE EXCEPTION 'UNKNOWN_UNIT_TYPE';
  END IF;
  RETURN NEW;
END
$function$;
CREATE TRIGGER agents_validate_unit_role_v1
BEFORE INSERT OR UPDATE OF agent_key,unit_key,role_kind ON bt2.agents
FOR EACH ROW EXECUTE FUNCTION bt2.validate_agent_unit_role_v1();

CREATE OR REPLACE FUNCTION bt2.validate_agent_relationship_v1()
RETURNS trigger LANGUAGE plpgsql AS $function$
DECLARE s record; t record; u record;
BEGIN
  SELECT * INTO STRICT s FROM bt2.agents WHERE agent_key=NEW.source_agent_key;
  SELECT * INTO STRICT t FROM bt2.agents WHERE agent_key=NEW.target_agent_key;
  IF NEW.relation_type='ORCHESTRATES' THEN
    IF s.unit_key<>t.unit_key OR t.role_kind<>'SUBAGENT' THEN RAISE EXCEPTION 'INVALID_ORCHESTRATION_EDGE'; END IF;
    SELECT * INTO STRICT u FROM bt2.agent_units WHERE unit_key=s.unit_key;
    IF u.unit_type<>'ORCHESTRATED_TEAM' OR u.orchestrator_agent_key<>s.agent_key OR s.role_kind<>'PRIMARY' THEN RAISE EXCEPTION 'INVALID_ORCHESTRATOR'; END IF;
  ELSIF NEW.relation_type='PAIRED_WITH' THEN
    IF s.unit_key<>t.unit_key OR s.role_kind<>'PAIRED' OR t.role_kind<>'PAIRED' THEN RAISE EXCEPTION 'INVALID_PAIR_EDGE'; END IF;
    SELECT * INTO STRICT u FROM bt2.agent_units WHERE unit_key=s.unit_key;
    IF u.unit_type<>'PAIRED_TEAM' THEN RAISE EXCEPTION 'INVALID_PAIR_UNIT'; END IF;
  ELSIF NEW.relation_type='COORDINATES_WITH' THEN
    NULL;
  ELSE
    RAISE EXCEPTION 'UNKNOWN_RELATION_TYPE';
  END IF;
  RETURN NEW;
END
$function$;
CREATE TRIGGER agent_relationships_validate_v1
BEFORE INSERT OR UPDATE OF source_agent_key,target_agent_key,relation_type,active ON bt2.agent_relationships
FOR EACH ROW EXECUTE FUNCTION bt2.validate_agent_relationship_v1();
CREATE UNIQUE INDEX agent_relationships_one_active_orchestrator_per_target_v1
  ON bt2.agent_relationships(target_agent_key)
  WHERE active AND relation_type='ORCHESTRATES';

-- 3. Training package, qualification and checkpoint identities must agree.
ALTER TABLE bt2.training_packages
  ADD CONSTRAINT training_packages_id_agent_key_uniq UNIQUE (training_package_id,agent_key);
ALTER TABLE bt2.training_qualifications
  DROP CONSTRAINT training_qualifications_training_package_id_fkey;
ALTER TABLE bt2.training_qualifications
  ADD CONSTRAINT training_qualifications_package_agent_fkey
  FOREIGN KEY (training_package_id,agent_key)
  REFERENCES bt2.training_packages(training_package_id,agent_key);
ALTER TABLE bt2.training_qualifications
  ADD CONSTRAINT training_qualifications_identity_uniq
  UNIQUE (qualification_id,agent_key,training_package_id);

ALTER TABLE bt2.operational_checkpoints ADD COLUMN generation bigint NOT NULL DEFAULT 1;
ALTER TABLE bt2.operational_checkpoints ADD COLUMN runtime_session_id uuid REFERENCES bt2.runtime_sessions(runtime_session_id);
ALTER TABLE bt2.operational_checkpoints
  ADD CONSTRAINT operational_checkpoints_generation_check CHECK (generation>=1);
ALTER TABLE bt2.operational_checkpoints
  ADD CONSTRAINT operational_checkpoints_agent_generation_uniq UNIQUE (agent_key,generation);
ALTER TABLE bt2.operational_checkpoints
  ADD CONSTRAINT operational_checkpoints_id_agent_uniq UNIQUE (checkpoint_id,agent_key);
ALTER TABLE bt2.operational_checkpoints
  ADD CONSTRAINT operational_checkpoints_qualification_requires_package
  CHECK (qualification_id IS NULL OR training_package_id IS NOT NULL);
ALTER TABLE bt2.operational_checkpoints DROP CONSTRAINT operational_checkpoints_predecessor_checkpoint_id_fkey;
ALTER TABLE bt2.operational_checkpoints DROP CONSTRAINT operational_checkpoints_training_package_id_fkey;
ALTER TABLE bt2.operational_checkpoints DROP CONSTRAINT operational_checkpoints_qualification_id_fkey;
ALTER TABLE bt2.operational_checkpoints
  ADD CONSTRAINT operational_checkpoints_same_agent_predecessor_fkey
  FOREIGN KEY (predecessor_checkpoint_id,agent_key)
  REFERENCES bt2.operational_checkpoints(checkpoint_id,agent_key);
ALTER TABLE bt2.operational_checkpoints
  ADD CONSTRAINT operational_checkpoints_package_agent_fkey
  FOREIGN KEY (training_package_id,agent_key)
  REFERENCES bt2.training_packages(training_package_id,agent_key);
ALTER TABLE bt2.operational_checkpoints
  ADD CONSTRAINT operational_checkpoints_qualification_identity_fkey
  FOREIGN KEY (qualification_id,agent_key,training_package_id)
  REFERENCES bt2.training_qualifications(qualification_id,agent_key,training_package_id);

CREATE OR REPLACE FUNCTION bt2.validate_operational_checkpoint_lineage_v1()
RETURNS trigger LANGUAGE plpgsql AS $function$
DECLARE v_parent_generation bigint;
BEGIN
  IF NEW.predecessor_checkpoint_id IS NULL THEN
    IF NEW.generation<>1 THEN RAISE EXCEPTION 'ROOT_CHECKPOINT_GENERATION_MUST_BE_1'; END IF;
  ELSE
    SELECT generation INTO v_parent_generation
    FROM bt2.operational_checkpoints
    WHERE checkpoint_id=NEW.predecessor_checkpoint_id AND agent_key=NEW.agent_key;
    IF NOT FOUND THEN RAISE EXCEPTION 'CHECKPOINT_PREDECESSOR_IDENTITY_MISMATCH'; END IF;
    IF NEW.generation<>v_parent_generation+1 THEN RAISE EXCEPTION 'NONCONTIGUOUS_CHECKPOINT_GENERATION'; END IF;
  END IF;
  RETURN NEW;
END
$function$;
CREATE TRIGGER operational_checkpoints_validate_lineage_v1
BEFORE INSERT ON bt2.operational_checkpoints
FOR EACH ROW EXECUTE FUNCTION bt2.validate_operational_checkpoint_lineage_v1();

-- 4. Workspace checkpoint chain is same-workspace, linear and CAS-bound to HEAD generation.
ALTER TABLE bt2.workspace_checkpoints
  ADD CONSTRAINT workspace_checkpoints_id_workspace_uniq UNIQUE (workspace_checkpoint_id,workspace_id);
ALTER TABLE bt2.workspace_checkpoints DROP CONSTRAINT workspace_checkpoints_predecessor_checkpoint_id_fkey;
ALTER TABLE bt2.workspace_checkpoints
  ADD CONSTRAINT workspace_checkpoints_same_workspace_predecessor_fkey
  FOREIGN KEY (predecessor_checkpoint_id,workspace_id)
  REFERENCES bt2.workspace_checkpoints(workspace_checkpoint_id,workspace_id);

CREATE OR REPLACE FUNCTION bt2.guard_workspace_generation_v1()
RETURNS trigger LANGUAGE plpgsql AS $function$
BEGIN
  IF NEW.generation<>OLD.generation AND coalesce(current_setting('bt2.workspace_checkpoint_writer',true),'')<>'on' THEN
    RAISE EXCEPTION 'WORKSPACE_GENERATION_IS_CHECKPOINT_PROJECTION';
  END IF;
  RETURN NEW;
END
$function$;
CREATE TRIGGER workspaces_guard_generation_v1
BEFORE UPDATE OF generation ON bt2.workspaces
FOR EACH ROW EXECUTE FUNCTION bt2.guard_workspace_generation_v1();

CREATE OR REPLACE FUNCTION bt2.advance_workspace_checkpoint_v1()
RETURNS trigger LANGUAGE plpgsql AS $function$
DECLARE v_current bigint; v_head uuid;
BEGIN
  SELECT generation INTO STRICT v_current FROM bt2.workspaces WHERE workspace_id=NEW.workspace_id FOR UPDATE;
  IF NEW.generation<>v_current+1 THEN RAISE EXCEPTION 'STALE_WORKSPACE_GENERATION'; END IF;
  IF v_current=0 THEN
    IF NEW.predecessor_checkpoint_id IS NOT NULL THEN RAISE EXCEPTION 'FIRST_CHECKPOINT_MUST_BE_ROOT'; END IF;
  ELSE
    SELECT workspace_checkpoint_id INTO STRICT v_head FROM bt2.workspace_checkpoints WHERE workspace_id=NEW.workspace_id AND generation=v_current;
    IF NEW.predecessor_checkpoint_id IS DISTINCT FROM v_head THEN RAISE EXCEPTION 'CHECKPOINT_PREDECESSOR_NOT_CURRENT_HEAD'; END IF;
  END IF;
  PERFORM set_config('bt2.workspace_checkpoint_writer','on',true);
  UPDATE bt2.workspaces SET generation=NEW.generation,updated_at=clock_timestamp() WHERE workspace_id=NEW.workspace_id;
  PERFORM set_config('bt2.workspace_checkpoint_writer','off',true);
  RETURN NEW;
END
$function$;
CREATE TRIGGER workspace_checkpoints_advance_head_v1
BEFORE INSERT ON bt2.workspace_checkpoints
FOR EACH ROW EXECUTE FUNCTION bt2.advance_workspace_checkpoint_v1();

CREATE OR REPLACE FUNCTION bt2.prevent_append_only_history_mutation_v1()
RETURNS trigger LANGUAGE plpgsql AS $function$
BEGIN
  RAISE EXCEPTION 'APPEND_ONLY_HISTORY';
END
$function$;
CREATE TRIGGER operational_checkpoints_append_only_v1
BEFORE UPDATE OR DELETE ON bt2.operational_checkpoints
FOR EACH ROW EXECUTE FUNCTION bt2.prevent_append_only_history_mutation_v1();
CREATE TRIGGER workspace_checkpoints_append_only_v1
BEFORE UPDATE OR DELETE ON bt2.workspace_checkpoints
FOR EACH ROW EXECUTE FUNCTION bt2.prevent_append_only_history_mutation_v1();

-- 5. WIP external-effect history is an append-only event chain; operations is only the current projection.
ALTER TABLE bt2.operations DROP CONSTRAINT operations_state_check;
ALTER TABLE bt2.operations
  ADD CONSTRAINT operations_state_check CHECK (state IN ('PREPARED','ATTEMPTED','VERIFIED','FAILED','AMBIGUOUS','RECONCILED'));
ALTER TABLE bt2.operations ADD COLUMN latest_event_id uuid;
ALTER TABLE bt2.operations ADD COLUMN actor_runtime_session_id uuid REFERENCES bt2.runtime_sessions(runtime_session_id);
ALTER TABLE bt2.operations ADD COLUMN effect_receipt jsonb;
ALTER TABLE bt2.operations ADD COLUMN result_summary text;

CREATE TABLE bt2.operation_events (
  operation_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  operation_id uuid NOT NULL REFERENCES bt2.operations(operation_id),
  sequence integer NOT NULL CHECK (sequence>=1),
  state text NOT NULL CHECK (state IN ('PREPARED','ATTEMPTED','VERIFIED','FAILED','AMBIGUOUS','RECONCILED')),
  previous_event_id uuid,
  runtime_session_id uuid REFERENCES bt2.runtime_sessions(runtime_session_id),
  recovery_instruction text NOT NULL CHECK (recovery_instruction IN ('inspect_before_retry','no_retry_required')),
  result_summary text,
  result_payload jsonb,
  result_digest_sha256 text CHECK (result_digest_sha256 IS NULL OR result_digest_sha256 ~ '^[0-9a-f]{64}$'),
  effect_receipt jsonb,
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT operation_events_sequence_root_check CHECK ((sequence=1)=(previous_event_id IS NULL)),
  CONSTRAINT operation_events_verified_receipt_check CHECK (state NOT IN ('VERIFIED','RECONCILED') OR (effect_receipt IS NOT NULL AND result_summary IS NOT NULL)),
  CONSTRAINT operation_events_operation_sequence_uniq UNIQUE (operation_id,sequence),
  CONSTRAINT operation_events_id_operation_uniq UNIQUE (operation_event_id,operation_id),
  CONSTRAINT operation_events_id_operation_state_uniq UNIQUE (operation_event_id,operation_id,state),
  CONSTRAINT operation_events_one_successor_uniq UNIQUE (previous_event_id),
  CONSTRAINT operation_events_same_operation_predecessor_fkey FOREIGN KEY (previous_event_id,operation_id)
    REFERENCES bt2.operation_events(operation_event_id,operation_id)
);
CREATE UNIQUE INDEX operation_events_one_root_per_operation_v1
  ON bt2.operation_events(operation_id) WHERE previous_event_id IS NULL;
CREATE TRIGGER operation_events_append_only_v1
BEFORE UPDATE OR DELETE ON bt2.operation_events
FOR EACH ROW EXECUTE FUNCTION bt2.prevent_append_only_history_mutation_v1();

-- No operation rows existed at the migration cut, so projection/event binding can be made mandatory without synthetic history.
ALTER TABLE bt2.operations ALTER COLUMN latest_event_id SET NOT NULL;
ALTER TABLE bt2.operations
  ADD CONSTRAINT operations_latest_event_projection_fkey
  FOREIGN KEY (latest_event_id,operation_id,state)
  REFERENCES bt2.operation_events(operation_event_id,operation_id,state)
  DEFERRABLE INITIALLY DEFERRED;

CREATE OR REPLACE FUNCTION bt2.prepare_operation_v1(
  p_operation_id uuid,
  p_workspace_id uuid,
  p_actor_agent_key text,
  p_actor_runtime_session_id uuid,
  p_operation_kind text,
  p_target_locator text,
  p_idempotency_key text,
  p_request_payload jsonb
) RETURNS uuid LANGUAGE plpgsql AS $function$
DECLARE v_subject jsonb; v_digest text; v_existing record; v_event uuid:=gen_random_uuid();
BEGIN
  PERFORM pg_advisory_xact_lock(hashtextextended(p_operation_id::text,0));
  IF p_request_payload IS NULL THEN RAISE EXCEPTION 'INVALID_REQUEST_PAYLOAD'; END IF;
  v_subject:=jsonb_build_object('workspace_id',p_workspace_id,'actor_agent_key',p_actor_agent_key,'operation_kind',p_operation_kind,'target_locator',p_target_locator,'idempotency_key',p_idempotency_key,'request_payload',p_request_payload);
  v_digest:=encode(digest(convert_to(v_subject::text,'UTF8'),'sha256'),'hex');
  SELECT * INTO v_existing FROM bt2.operations WHERE operation_id=p_operation_id;
  IF FOUND THEN
    IF v_existing.request_digest_sha256<>v_digest THEN RAISE EXCEPTION 'OPERATION_ID_REUSE_CONFLICT'; END IF;
    RETURN v_existing.latest_event_id;
  END IF;
  INSERT INTO bt2.operations(operation_id,workspace_id,actor_agent_key,actor_runtime_session_id,operation_kind,target_locator,idempotency_key,request_digest_sha256,request_payload,state,latest_event_id,do_not_repeat)
  VALUES(p_operation_id,p_workspace_id,p_actor_agent_key,p_actor_runtime_session_id,p_operation_kind,p_target_locator,p_idempotency_key,v_digest,p_request_payload,'PREPARED',v_event,true);
  INSERT INTO bt2.operation_events(operation_event_id,operation_id,sequence,state,previous_event_id,runtime_session_id,recovery_instruction)
  VALUES(v_event,p_operation_id,1,'PREPARED',NULL,p_actor_runtime_session_id,'inspect_before_retry');
  RETURN v_event;
END
$function$;

CREATE OR REPLACE FUNCTION bt2.append_operation_event_v1(
  p_operation_id uuid,
  p_previous_event_id uuid,
  p_state text,
  p_runtime_session_id uuid,
  p_recovery_instruction text,
  p_result_summary text DEFAULT NULL,
  p_result_payload jsonb DEFAULT NULL,
  p_effect_receipt jsonb DEFAULT NULL
) RETURNS uuid LANGUAGE plpgsql AS $function$
DECLARE v_op record; v_prev record; v_event uuid:=gen_random_uuid(); v_next integer; v_state text:=upper(btrim(p_state)); v_result_digest text;
BEGIN
  SELECT * INTO STRICT v_op FROM bt2.operations WHERE operation_id=p_operation_id FOR UPDATE;
  SELECT * INTO STRICT v_prev FROM bt2.operation_events WHERE operation_event_id=v_op.latest_event_id AND operation_id=p_operation_id;
  IF p_previous_event_id IS DISTINCT FROM v_prev.operation_event_id THEN RAISE EXCEPTION 'STALE_OPERATION_EVENT'; END IF;
  IF NOT (
      (v_prev.state='PREPARED' AND v_state IN ('ATTEMPTED','FAILED','AMBIGUOUS')) OR
      (v_prev.state='ATTEMPTED' AND v_state IN ('VERIFIED','FAILED','AMBIGUOUS')) OR
      (v_prev.state='AMBIGUOUS' AND v_state='RECONCILED')
    ) THEN RAISE EXCEPTION 'INVALID_OPERATION_TRANSITION';
  END IF;
  IF v_state IN ('VERIFIED','RECONCILED') AND (p_effect_receipt IS NULL OR p_result_summary IS NULL) THEN RAISE EXCEPTION 'VERIFIED_EFFECT_REQUIRES_RECEIPT'; END IF;
  IF p_recovery_instruction NOT IN ('inspect_before_retry','no_retry_required') THEN RAISE EXCEPTION 'INVALID_RECOVERY_INSTRUCTION'; END IF;
  v_next:=v_prev.sequence+1;
  IF p_result_payload IS NOT NULL THEN v_result_digest:=encode(digest(convert_to(p_result_payload::text,'UTF8'),'sha256'),'hex'); END IF;
  INSERT INTO bt2.operation_events(operation_event_id,operation_id,sequence,state,previous_event_id,runtime_session_id,recovery_instruction,result_summary,result_payload,result_digest_sha256,effect_receipt)
  VALUES(v_event,p_operation_id,v_next,v_state,v_prev.operation_event_id,p_runtime_session_id,p_recovery_instruction,p_result_summary,p_result_payload,v_result_digest,p_effect_receipt);
  UPDATE bt2.operations SET state=v_state,latest_event_id=v_event,
    attempted_at=CASE WHEN v_state='ATTEMPTED' AND attempted_at IS NULL THEN clock_timestamp() ELSE attempted_at END,
    resolved_at=CASE WHEN v_state IN ('VERIFIED','FAILED','RECONCILED') THEN clock_timestamp() ELSE resolved_at END,
    result_payload=COALESCE(p_result_payload,result_payload),
    result_digest_sha256=COALESCE(v_result_digest,result_digest_sha256),
    effect_receipt=COALESCE(p_effect_receipt,effect_receipt),
    result_summary=COALESCE(p_result_summary,result_summary),
    do_not_repeat=(v_state<>'FAILED'),updated_at=clock_timestamp()
  WHERE operation_id=p_operation_id;
  RETURN v_event;
END
$function$;
