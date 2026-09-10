-- BT2 training qualification/current-activation integrity V1.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.
-- Qualification and installation observations remain historical evidence;
-- current effectiveness is derived and fails closed when support becomes stale.

CREATE OR REPLACE FUNCTION bt2.reject_training_qualification_mutation_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
BEGIN
  RAISE EXCEPTION 'TRAINING_QUALIFICATION_HISTORY_IS_APPEND_ONLY';
END
$function$;

CREATE TRIGGER training_qualifications_no_update_v1
BEFORE UPDATE OR DELETE ON bt2.training_qualifications
FOR EACH ROW EXECUTE FUNCTION bt2.reject_training_qualification_mutation_v1();

CREATE OR REPLACE VIEW bt2.training_qualification_current_v1 AS
SELECT DISTINCT ON (q.agent_key,q.training_package_id)
  q.qualification_id,
  q.agent_key,
  q.training_package_id,
  q.outcome,
  q.evaluator,
  q.evidence,
  q.qualified_at
FROM bt2.training_qualifications q
ORDER BY q.agent_key,q.training_package_id,q.qualified_at DESC,q.qualification_id DESC;

CREATE OR REPLACE FUNCTION bt2.guard_training_package_qualified_base_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
DECLARE v_current record;
BEGIN
  IF NEW.status='QUALIFIED_BASE' THEN
    IF NEW.compatibility_state <> 'COMPATIBLE' THEN
      RAISE EXCEPTION 'QUALIFIED_BASE_REQUIRES_COMPATIBLE_PASS_EVIDENCE';
    END IF;

    SELECT q.qualification_id,q.outcome
    INTO v_current
    FROM bt2.training_qualification_current_v1 q
    WHERE q.training_package_id=NEW.training_package_id
      AND q.agent_key=NEW.agent_key;

    IF NOT FOUND OR v_current.outcome<>'PASS' THEN
      RAISE EXCEPTION 'QUALIFIED_BASE_REQUIRES_COMPATIBLE_PASS_EVIDENCE';
    END IF;
  END IF;
  RETURN NEW;
END
$function$;

CREATE OR REPLACE FUNCTION bt2.guard_training_installation_event_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
DECLARE
  v_prev record;
  v_package record;
  v_current_qualification record;
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

    SELECT q.qualification_id,q.outcome
    INTO v_current_qualification
    FROM bt2.training_qualification_current_v1 q
    WHERE q.training_package_id=NEW.training_package_id
      AND q.agent_key=NEW.agent_key;

    IF NOT FOUND
       OR v_current_qualification.outcome<>'PASS'
       OR NEW.qualification_id IS DISTINCT FROM v_current_qualification.qualification_id THEN
      RAISE EXCEPTION 'ACTIVE_TRAINING_REQUIRES_CURRENT_PASS_QUALIFICATION';
    END IF;

    IF EXISTS (
      SELECT 1
      FROM bt2.training_installation_current_v1 current_i
      JOIN bt2.training_packages current_p
        ON current_p.training_package_id=current_i.training_package_id
       AND current_p.agent_key=current_i.agent_key
      LEFT JOIN bt2.training_qualification_current_v1 current_q
        ON current_q.training_package_id=current_i.training_package_id
       AND current_q.agent_key=current_i.agent_key
      LEFT JOIN bt2.runtime_sessions current_rs
        ON current_rs.runtime_session_id=current_i.runtime_session_id
       AND current_rs.agent_key=current_i.agent_key
      WHERE current_i.agent_key=NEW.agent_key
        AND current_i.binding_id<>NEW.binding_id
        AND current_i.observed_state='ACTIVE'
        AND current_p.status='QUALIFIED_BASE'
        AND current_p.compatibility_state='COMPATIBLE'
        AND current_q.outcome='PASS'
        AND current_q.qualification_id=current_i.qualification_id
        AND (current_i.target_kind<>'RUNTIME_SESSION' OR current_rs.status='ACTIVE')
    ) THEN
      RAISE EXCEPTION 'AGENT_ALREADY_HAS_ACTIVE_TRAINING_BINDING';
    END IF;
  END IF;

  RETURN NEW;
END
$function$;

CREATE OR REPLACE VIEW bt2.training_installation_effective_v1 AS
SELECT
  i.*,
  CASE
    WHEN i.observed_state<>'ACTIVE' THEN NULL::boolean
    ELSE (
      p.status='QUALIFIED_BASE'
      AND p.compatibility_state='COMPATIBLE'
      AND q.outcome='PASS'
      AND q.qualification_id=i.qualification_id
      AND (i.target_kind<>'RUNTIME_SESSION' OR rs.status='ACTIVE')
    )
  END AS activation_currently_valid,
  CASE
    WHEN i.observed_state='ACTIVE' AND NOT (
      p.status='QUALIFIED_BASE'
      AND p.compatibility_state='COMPATIBLE'
      AND q.outcome='PASS'
      AND q.qualification_id=i.qualification_id
      AND (i.target_kind<>'RUNTIME_SESSION' OR rs.status='ACTIVE')
    ) THEN 'INVALIDATED'
    ELSE i.observed_state
  END AS effective_state
FROM bt2.training_installation_current_v1 i
JOIN bt2.training_packages p
  ON p.training_package_id=i.training_package_id
 AND p.agent_key=i.agent_key
LEFT JOIN bt2.training_qualification_current_v1 q
  ON q.training_package_id=i.training_package_id
 AND q.agent_key=i.agent_key
LEFT JOIN bt2.runtime_sessions rs
  ON rs.runtime_session_id=i.runtime_session_id
 AND rs.agent_key=i.agent_key;

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
  i.observed_state AS runtime_installation_observed_state,
  i.activation_currently_valid,
  i.effective_state AS runtime_installation_effective_state,
  i.observed_at AS runtime_installation_observed_at
FROM bt2.agents a
LEFT JOIN bt2.training_packages tp ON tp.agent_key=a.agent_key
LEFT JOIN bt2.training_qualification_current_v1 q
  ON q.training_package_id=tp.training_package_id
 AND q.agent_key=a.agent_key
LEFT JOIN LATERAL (
  SELECT ti.*
  FROM bt2.training_installation_effective_v1 ti
  WHERE ti.training_package_id=tp.training_package_id
    AND ti.agent_key=a.agent_key
  ORDER BY (ti.effective_state='ACTIVE') DESC,ti.observed_at DESC,ti.installation_event_id DESC
  LIMIT 1
) i ON true;
