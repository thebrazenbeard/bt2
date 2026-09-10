-- BT2 training installation evidence V1.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.
-- This schema records observed installation/activation evidence only.
-- It does not itself install, activate, or modify any external runtime.
-- History is append-only; current state is derived from the event chain.

CREATE TABLE bt2.training_installation_events (
  installation_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  binding_id uuid NOT NULL,
  agent_key text NOT NULL,
  training_package_id uuid NOT NULL,
  qualification_id uuid,
  target_kind text NOT NULL,
  target_locator text,
  runtime_session_id uuid,
  sequence bigint NOT NULL,
  previous_event_id uuid,
  observed_state text NOT NULL,
  evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
  observed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT training_installation_events_id_binding_uniq
    UNIQUE (installation_event_id,binding_id),
  CONSTRAINT training_installation_events_binding_sequence_uniq
    UNIQUE (binding_id,sequence),
  CONSTRAINT training_installation_events_sequence_check
    CHECK (sequence >= 1),
  CONSTRAINT training_installation_events_root_shape_check
    CHECK ((sequence=1)=(previous_event_id IS NULL)),
  CONSTRAINT training_installation_events_target_kind_check
    CHECK (target_kind IN ('CHATGPT_PROJECT','RUNTIME_SESSION','EXTERNAL_RUNTIME','OTHER')),
  CONSTRAINT training_installation_events_observed_state_check
    CHECK (observed_state IN ('STAGED','INSTALLED','ACTIVE','INACTIVE','REMOVED')),
  CONSTRAINT training_installation_events_runtime_target_shape_check
    CHECK (
      (target_kind='RUNTIME_SESSION' AND runtime_session_id IS NOT NULL)
      OR
      (target_kind<>'RUNTIME_SESSION' AND runtime_session_id IS NULL AND target_locator IS NOT NULL AND btrim(target_locator)<>'')
    ),
  CONSTRAINT training_installation_events_active_shape_check
    CHECK (observed_state<>'ACTIVE' OR (qualification_id IS NOT NULL AND evidence <> '{}'::jsonb)),
  CONSTRAINT training_installation_events_package_agent_fkey
    FOREIGN KEY (training_package_id,agent_key)
    REFERENCES bt2.training_packages(training_package_id,agent_key),
  CONSTRAINT training_installation_events_qualification_identity_fkey
    FOREIGN KEY (qualification_id,agent_key,training_package_id)
    REFERENCES bt2.training_qualifications(qualification_id,agent_key,training_package_id),
  CONSTRAINT training_installation_events_runtime_same_agent_fkey
    FOREIGN KEY (runtime_session_id,agent_key)
    REFERENCES bt2.runtime_sessions(runtime_session_id,agent_key),
  CONSTRAINT training_installation_events_same_binding_predecessor_fkey
    FOREIGN KEY (previous_event_id,binding_id)
    REFERENCES bt2.training_installation_events(installation_event_id,binding_id)
);

CREATE UNIQUE INDEX training_installation_events_one_successor
  ON bt2.training_installation_events(previous_event_id)
  WHERE previous_event_id IS NOT NULL;

CREATE OR REPLACE FUNCTION bt2.reject_training_installation_event_mutation_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
BEGIN
  RAISE EXCEPTION 'TRAINING_INSTALLATION_HISTORY_IS_APPEND_ONLY';
END
$function$;

CREATE TRIGGER training_installation_events_no_update_v1
BEFORE UPDATE OR DELETE ON bt2.training_installation_events
FOR EACH ROW EXECUTE FUNCTION bt2.reject_training_installation_event_mutation_v1();

CREATE OR REPLACE FUNCTION bt2.guard_training_installation_event_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
DECLARE
  v_prev record;
  v_package record;
  v_qualification record;
BEGIN
  PERFORM pg_advisory_xact_lock(hashtextextended('training-installation:'||NEW.agent_key,0));

  IF NEW.previous_event_id IS NULL THEN
    IF NEW.sequence<>1 THEN
      RAISE EXCEPTION 'TRAINING_INSTALLATION_ROOT_SEQUENCE_INVALID';
    END IF;
    IF NEW.observed_state NOT IN ('STAGED','INSTALLED','ACTIVE') THEN
      RAISE EXCEPTION 'TRAINING_INSTALLATION_ROOT_STATE_INVALID';
    END IF;
  ELSE
    SELECT * INTO STRICT v_prev
    FROM bt2.training_installation_events e
    WHERE e.installation_event_id=NEW.previous_event_id
      AND e.binding_id=NEW.binding_id;

    IF NEW.sequence<>v_prev.sequence+1 THEN
      RAISE EXCEPTION 'TRAINING_INSTALLATION_SEQUENCE_INVALID';
    END IF;

    IF NEW.agent_key IS DISTINCT FROM v_prev.agent_key
       OR NEW.training_package_id IS DISTINCT FROM v_prev.training_package_id
       OR NEW.target_kind IS DISTINCT FROM v_prev.target_kind
       OR NEW.target_locator IS DISTINCT FROM v_prev.target_locator
       OR NEW.runtime_session_id IS DISTINCT FROM v_prev.runtime_session_id THEN
      RAISE EXCEPTION 'TRAINING_INSTALLATION_BINDING_SUBJECT_CHANGED';
    END IF;

    IF NOT (
      (v_prev.observed_state='STAGED' AND NEW.observed_state IN ('INSTALLED','REMOVED'))
      OR (v_prev.observed_state='INSTALLED' AND NEW.observed_state IN ('ACTIVE','INACTIVE','REMOVED'))
      OR (v_prev.observed_state='ACTIVE' AND NEW.observed_state IN ('INACTIVE','REMOVED'))
      OR (v_prev.observed_state='INACTIVE' AND NEW.observed_state IN ('INSTALLED','ACTIVE','REMOVED'))
    ) THEN
      RAISE EXCEPTION 'TRAINING_INSTALLATION_TRANSITION_INVALID';
    END IF;
  END IF;

  IF NEW.observed_state='ACTIVE' THEN
    SELECT tp.status,tp.compatibility_state
    INTO STRICT v_package
    FROM bt2.training_packages tp
    WHERE tp.training_package_id=NEW.training_package_id
      AND tp.agent_key=NEW.agent_key;

    IF v_package.status<>'QUALIFIED_BASE'
       OR v_package.compatibility_state<>'COMPATIBLE' THEN
      RAISE EXCEPTION 'ACTIVE_TRAINING_REQUIRES_COMPATIBLE_QUALIFIED_BASE';
    END IF;

    SELECT tq.outcome
    INTO STRICT v_qualification
    FROM bt2.training_qualifications tq
    WHERE tq.qualification_id=NEW.qualification_id
      AND tq.training_package_id=NEW.training_package_id
      AND tq.agent_key=NEW.agent_key;

    IF v_qualification.outcome<>'PASS' THEN
      RAISE EXCEPTION 'ACTIVE_TRAINING_REQUIRES_PASS_QUALIFICATION';
    END IF;

    IF EXISTS (
      SELECT 1
      FROM bt2.training_installation_events e
      WHERE e.agent_key=NEW.agent_key
        AND e.observed_state='ACTIVE'
        AND e.binding_id<>NEW.binding_id
        AND NOT EXISTS (
          SELECT 1 FROM bt2.training_installation_events child
          WHERE child.previous_event_id=e.installation_event_id
        )
    ) THEN
      RAISE EXCEPTION 'AGENT_ALREADY_HAS_ACTIVE_TRAINING_BINDING';
    END IF;
  END IF;

  RETURN NEW;
END
$function$;

CREATE TRIGGER training_installation_events_guard_v1
BEFORE INSERT ON bt2.training_installation_events
FOR EACH ROW EXECUTE FUNCTION bt2.guard_training_installation_event_v1();

CREATE OR REPLACE FUNCTION bt2.begin_training_installation_evidence_v1(
  p_agent_key text,
  p_training_package_id uuid,
  p_qualification_id uuid,
  p_target_kind text,
  p_target_locator text,
  p_runtime_session_id uuid,
  p_observed_state text,
  p_evidence jsonb
) RETURNS TABLE(out_binding_id uuid,out_event_id uuid)
LANGUAGE plpgsql
AS $function$
DECLARE
  v_binding uuid:=gen_random_uuid();
  v_event uuid:=gen_random_uuid();
BEGIN
  INSERT INTO bt2.training_installation_events(
    installation_event_id,binding_id,agent_key,training_package_id,qualification_id,
    target_kind,target_locator,runtime_session_id,sequence,previous_event_id,
    observed_state,evidence
  ) VALUES(
    v_event,v_binding,p_agent_key,p_training_package_id,p_qualification_id,
    upper(btrim(p_target_kind)),p_target_locator,p_runtime_session_id,1,NULL,
    upper(btrim(p_observed_state)),coalesce(p_evidence,'{}'::jsonb)
  );
  RETURN QUERY SELECT v_binding,v_event;
END
$function$;

CREATE OR REPLACE FUNCTION bt2.append_training_installation_evidence_v1(
  p_previous_event_id uuid,
  p_qualification_id uuid,
  p_observed_state text,
  p_evidence jsonb
) RETURNS uuid
LANGUAGE plpgsql
AS $function$
DECLARE
  v_prev record;
  v_event uuid:=gen_random_uuid();
BEGIN
  SELECT * INTO STRICT v_prev
  FROM bt2.training_installation_events e
  WHERE e.installation_event_id=p_previous_event_id;

  INSERT INTO bt2.training_installation_events(
    installation_event_id,binding_id,agent_key,training_package_id,qualification_id,
    target_kind,target_locator,runtime_session_id,sequence,previous_event_id,
    observed_state,evidence
  ) VALUES(
    v_event,v_prev.binding_id,v_prev.agent_key,v_prev.training_package_id,p_qualification_id,
    v_prev.target_kind,v_prev.target_locator,v_prev.runtime_session_id,v_prev.sequence+1,
    v_prev.installation_event_id,upper(btrim(p_observed_state)),coalesce(p_evidence,'{}'::jsonb)
  );

  RETURN v_event;
END
$function$;

CREATE OR REPLACE VIEW bt2.training_installation_current_v1 AS
SELECT DISTINCT ON (e.binding_id)
  e.binding_id,e.installation_event_id,e.agent_key,e.training_package_id,e.qualification_id,
  e.target_kind,e.target_locator,e.runtime_session_id,e.sequence,e.observed_state,e.evidence,e.observed_at
FROM bt2.training_installation_events e
ORDER BY e.binding_id,e.sequence DESC,e.installation_event_id DESC;

CREATE OR REPLACE VIEW bt2.agent_training_state_v1 AS
SELECT
  a.agent_key,
  tp.training_package_id,
  tp.version,
  tp.status AS package_status,
  tp.source_binding_state,
  tp.compatibility_state,
  q.qualification_id,
  q.outcome AS qualification_outcome,
  i.binding_id AS installation_binding_id,
  i.installation_event_id,
  i.target_kind,
  i.target_locator,
  i.runtime_session_id,
  i.observed_state AS runtime_installation_state,
  i.observed_at AS runtime_installation_observed_at
FROM bt2.agents a
LEFT JOIN bt2.training_packages tp ON tp.agent_key=a.agent_key
LEFT JOIN LATERAL (
  SELECT tq.qualification_id,tq.outcome,tq.qualified_at
  FROM bt2.training_qualifications tq
  WHERE tq.training_package_id=tp.training_package_id
    AND tq.agent_key=a.agent_key
  ORDER BY tq.qualified_at DESC,tq.qualification_id DESC
  LIMIT 1
) q ON true
LEFT JOIN LATERAL (
  SELECT ti.*
  FROM bt2.training_installation_current_v1 ti
  WHERE ti.training_package_id=tp.training_package_id
    AND ti.agent_key=a.agent_key
  ORDER BY (ti.observed_state='ACTIVE') DESC,ti.observed_at DESC,ti.installation_event_id DESC
  LIMIT 1
) i ON true;
