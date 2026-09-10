-- BT2 training installation evidence V1.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.
-- This schema records observed installation/activation evidence only.
-- It does not itself install, activate, or modify any external runtime.

CREATE TABLE bt2.training_installations (
  installation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_key text NOT NULL,
  training_package_id uuid NOT NULL,
  qualification_id uuid,
  target_kind text NOT NULL,
  target_locator text,
  runtime_session_id uuid,
  observed_state text NOT NULL,
  evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
  observed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  ended_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT training_installations_target_kind_check
    CHECK (target_kind IN ('CHATGPT_PROJECT','RUNTIME_SESSION','EXTERNAL_RUNTIME','OTHER')),
  CONSTRAINT training_installations_observed_state_check
    CHECK (observed_state IN ('STAGED','INSTALLED','ACTIVE','INACTIVE','REMOVED')),
  CONSTRAINT training_installations_runtime_target_shape_check
    CHECK (
      (target_kind='RUNTIME_SESSION' AND runtime_session_id IS NOT NULL)
      OR
      (target_kind<>'RUNTIME_SESSION' AND runtime_session_id IS NULL AND target_locator IS NOT NULL)
    ),
  CONSTRAINT training_installations_active_shape_check
    CHECK (
      observed_state<>'ACTIVE'
      OR (qualification_id IS NOT NULL AND ended_at IS NULL AND evidence <> '{}'::jsonb)
    ),
  CONSTRAINT training_installations_package_agent_fkey
    FOREIGN KEY (training_package_id,agent_key)
    REFERENCES bt2.training_packages(training_package_id,agent_key),
  CONSTRAINT training_installations_qualification_identity_fkey
    FOREIGN KEY (qualification_id,agent_key,training_package_id)
    REFERENCES bt2.training_qualifications(qualification_id,agent_key,training_package_id),
  CONSTRAINT training_installations_runtime_same_agent_fkey
    FOREIGN KEY (runtime_session_id,agent_key)
    REFERENCES bt2.runtime_sessions(runtime_session_id,agent_key)
);

CREATE UNIQUE INDEX training_installations_one_active_per_agent
  ON bt2.training_installations(agent_key)
  WHERE observed_state='ACTIVE';

CREATE OR REPLACE FUNCTION bt2.guard_training_installation_evidence_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
DECLARE
  v_package record;
  v_qualification record;
BEGIN
  NEW.updated_at:=clock_timestamp();

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
  END IF;

  RETURN NEW;
END
$function$;

CREATE TRIGGER training_installations_evidence_guard_v1
BEFORE INSERT OR UPDATE OF agent_key,training_package_id,qualification_id,target_kind,target_locator,runtime_session_id,observed_state,evidence,ended_at
ON bt2.training_installations
FOR EACH ROW EXECUTE FUNCTION bt2.guard_training_installation_evidence_v1();

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
  i.installation_id,
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
  SELECT ti.installation_id,ti.target_kind,ti.target_locator,ti.runtime_session_id,
         ti.observed_state,ti.observed_at
  FROM bt2.training_installations ti
  WHERE ti.training_package_id=tp.training_package_id
    AND ti.agent_key=a.agent_key
  ORDER BY (ti.observed_state='ACTIVE') DESC,ti.observed_at DESC,ti.installation_id DESC
  LIMIT 1
) i ON true;
