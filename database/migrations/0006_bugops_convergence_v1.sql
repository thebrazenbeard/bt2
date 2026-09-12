-- BT2 canonical BugOps convergence V1: schema layer.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.
-- Behavior/API definitions are installed by 0007 after this schema is complete.

-- Preserve independent defect, routing and dispatch generations.
ALTER TABLE bt2.bugs ADD COLUMN routing_revision bigint NOT NULL DEFAULT 1;
ALTER TABLE bt2.bugs ADD COLUMN dispatch_revision bigint NOT NULL DEFAULT 1;
ALTER TABLE bt2.bugs ADD CONSTRAINT bugs_routing_revision_check CHECK (routing_revision>0);
ALTER TABLE bt2.bugs ADD CONSTRAINT bugs_dispatch_revision_check CHECK (dispatch_revision>0);

ALTER TABLE bt2.bug_events ADD COLUMN routing_revision bigint NOT NULL DEFAULT 1;
ALTER TABLE bt2.bug_events ADD COLUMN dispatch_revision bigint NOT NULL DEFAULT 1;
ALTER TABLE bt2.bug_events ADD COLUMN request_digest_sha256 text;
ALTER TABLE bt2.bug_events ADD COLUMN request_payload jsonb;
ALTER TABLE bt2.bug_events ADD COLUMN dispatch_snapshot jsonb;
ALTER TABLE bt2.bug_events ADD COLUMN dispatch_payload_digest_sha256 text;
ALTER TABLE bt2.bug_events ADD CONSTRAINT bug_events_routing_revision_check CHECK (routing_revision>0);
ALTER TABLE bt2.bug_events ADD CONSTRAINT bug_events_dispatch_revision_check CHECK (dispatch_revision>0);
ALTER TABLE bt2.bug_events ADD CONSTRAINT bug_events_request_digest_check
  CHECK (request_digest_sha256 IS NULL OR request_digest_sha256 ~ '^[0-9a-f]{64}$');
ALTER TABLE bt2.bug_events ADD CONSTRAINT bug_events_dispatch_digest_check
  CHECK (dispatch_payload_digest_sha256 IS NULL OR dispatch_payload_digest_sha256 ~ '^[0-9a-f]{64}$');
CREATE TRIGGER bug_events_append_only_v1
BEFORE UPDATE OR DELETE ON bt2.bug_events
FOR EACH ROW EXECUTE FUNCTION bt2.prevent_append_only_history_mutation_v1();

-- Canonical severity follows BugOps Reporting Standard; legacy labels are normalized at API boundaries.
ALTER TABLE bt2.bugs DROP CONSTRAINT bugs_severity_check;
ALTER TABLE bt2.bugs ADD CONSTRAINT bugs_severity_check
  CHECK (severity IN ('SEV-0','SEV-1','SEV-2','SEV-3'));

CREATE OR REPLACE FUNCTION bt2.normalize_bug_severity_v1(p_severity text)
RETURNS text LANGUAGE plpgsql IMMUTABLE AS $function$
DECLARE v text:=upper(btrim(p_severity));
BEGIN
  RETURN CASE v
    WHEN 'SEV-0' THEN 'SEV-0' WHEN 'CRITICAL' THEN 'SEV-0'
    WHEN 'SEV-1' THEN 'SEV-1' WHEN 'HIGH' THEN 'SEV-1'
    WHEN 'SEV-2' THEN 'SEV-2' WHEN 'MEDIUM' THEN 'SEV-2'
    WHEN 'SEV-3' THEN 'SEV-3' WHEN 'LOW' THEN 'SEV-3'
    ELSE NULL
  END;
END
$function$;

-- Closure evidence is append-only and bound to the exact bug state version being closed.
CREATE TABLE bt2.bug_closure_evidence (
  closure_evidence_id uuid PRIMARY KEY,
  bug_id uuid NOT NULL REFERENCES bt2.bugs(bug_id),
  based_on_state_version bigint NOT NULL CHECK (based_on_state_version>0),
  mechanism_bounded boolean NOT NULL,
  corrective_controls_resolved boolean NOT NULL,
  regression_cases_present boolean NOT NULL,
  review_path_complete_or_exception boolean NOT NULL,
  claimed_effect_verified boolean NOT NULL,
  unresolved_hypotheses_explicit boolean NOT NULL,
  evidence jsonb NOT NULL,
  evidence_digest_sha256 text NOT NULL CHECK (evidence_digest_sha256 ~ '^[0-9a-f]{64}$'),
  recorded_by_agent_key text REFERENCES bt2.agents(agent_key),
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  UNIQUE (bug_id,based_on_state_version,closure_evidence_id)
);
CREATE TRIGGER bug_closure_evidence_append_only_v1
BEFORE UPDATE OR DELETE ON bt2.bug_closure_evidence
FOR EACH ROW EXECUTE FUNCTION bt2.prevent_append_only_history_mutation_v1();
