-- BT2 canonical PostgreSQL baseline captured from WoWSQL bt2-479e4ad9
-- Capture date: 2026-09-10
-- Review base: work/canonical-platform-consolidation-v1@32edb12f0f843639bece425b3d57ca784b2a76dc
-- Purpose: make the existing first-slice runtime schema reproducible before hardening.
-- This file intentionally reflects pre-hardening runtime state. Later migrations correct known integrity gaps.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS bt2;
CREATE SCHEMA IF NOT EXISTS bt2_legacy;

CREATE TABLE bt2.agent_units (
  unit_key text NOT NULL,
  display_name text NOT NULL,
  unit_type text NOT NULL,
  orchestrator_agent_key text,
  active boolean NOT NULL DEFAULT true,
  description text NOT NULL DEFAULT ''::text,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  updated_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT agent_units_pkey PRIMARY KEY (unit_key),
  CONSTRAINT agent_units_unit_type_check CHECK (unit_type = ANY (ARRAY['ORCHESTRATED_TEAM'::text, 'PAIRED_TEAM'::text, 'INDEPENDENT_AGENT'::text]))
);

CREATE TABLE bt2.agents (
  agent_key text NOT NULL,
  display_name text NOT NULL,
  numerical_identity integer,
  unit_key text NOT NULL,
  role_kind text NOT NULL,
  role_summary text NOT NULL,
  active boolean NOT NULL DEFAULT true,
  training_required boolean NOT NULL DEFAULT true,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  updated_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT agents_numerical_identity_key UNIQUE (numerical_identity),
  CONSTRAINT agents_pkey PRIMARY KEY (agent_key),
  CONSTRAINT agents_role_kind_check CHECK (role_kind = ANY (ARRAY['PRIMARY'::text, 'SUBAGENT'::text, 'PAIRED'::text, 'INDEPENDENT'::text])),
  CONSTRAINT agents_unit_key_fkey FOREIGN KEY (unit_key) REFERENCES bt2.agent_units(unit_key)
);

CREATE TABLE bt2.agent_relationships (
  relationship_id uuid NOT NULL DEFAULT gen_random_uuid(),
  source_agent_key text NOT NULL,
  target_agent_key text NOT NULL,
  relation_type text NOT NULL,
  active boolean NOT NULL DEFAULT true,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT agent_relationships_check CHECK (source_agent_key <> target_agent_key),
  CONSTRAINT agent_relationships_pkey PRIMARY KEY (relationship_id),
  CONSTRAINT agent_relationships_relation_type_check CHECK (relation_type = ANY (ARRAY['ORCHESTRATES'::text, 'PAIRED_WITH'::text, 'COORDINATES_WITH'::text])),
  CONSTRAINT agent_relationships_source_agent_key_fkey FOREIGN KEY (source_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT agent_relationships_source_agent_key_target_agent_key_relat_key UNIQUE (source_agent_key, target_agent_key, relation_type),
  CONSTRAINT agent_relationships_target_agent_key_fkey FOREIGN KEY (target_agent_key) REFERENCES bt2.agents(agent_key)
);

CREATE TABLE bt2.source_snapshots (
  source_snapshot_id uuid NOT NULL DEFAULT gen_random_uuid(),
  source_kind text NOT NULL,
  source_name text NOT NULL,
  canonical_locator text NOT NULL,
  source_ref text,
  source_commit text,
  source_tree text,
  visibility text,
  captured_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  evidence_class text NOT NULL DEFAULT 'OBSERVED'::text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  CONSTRAINT source_snapshots_pkey PRIMARY KEY (source_snapshot_id),
  CONSTRAINT source_snapshots_source_kind_source_name_source_ref_source__key UNIQUE (source_kind, source_name, source_ref, source_commit)
);

CREATE TABLE bt2.workspaces (
  workspace_id uuid NOT NULL DEFAULT gen_random_uuid(),
  workspace_key text NOT NULL,
  owner_agent_key text,
  status text NOT NULL,
  generation bigint NOT NULL DEFAULT 0,
  checkpoint_interval_calls integer NOT NULL DEFAULT 5,
  canonical_target jsonb NOT NULL DEFAULT '{}'::jsonb,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  updated_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT workspaces_checkpoint_interval_calls_check CHECK (checkpoint_interval_calls > 0),
  CONSTRAINT workspaces_generation_check CHECK (generation >= 0),
  CONSTRAINT workspaces_owner_agent_key_fkey FOREIGN KEY (owner_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT workspaces_pkey PRIMARY KEY (workspace_id),
  CONSTRAINT workspaces_status_check CHECK (status = ANY (ARRAY['ACTIVE'::text, 'PAUSED'::text, 'PROMOTED'::text, 'SHELVED'::text, 'SUPERSEDED'::text, 'ABANDONED'::text])),
  CONSTRAINT workspaces_workspace_key_key UNIQUE (workspace_key)
);

CREATE TABLE bt2.training_packages (
  training_package_id uuid NOT NULL DEFAULT gen_random_uuid(),
  agent_key text NOT NULL,
  version text NOT NULL,
  status text NOT NULL,
  source_repository text,
  source_ref text,
  source_commit text,
  source_tree text,
  manifest_path text,
  manifest_digest_sha256 text,
  source_set_digest_sha256 text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT training_packages_agent_key_fkey FOREIGN KEY (agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT training_packages_agent_key_version_source_set_digest_sha25_key UNIQUE (agent_key, version, source_set_digest_sha256),
  CONSTRAINT training_packages_manifest_digest_sha256_check CHECK (manifest_digest_sha256 IS NULL OR manifest_digest_sha256 ~ '^[0-9a-f]{64}$'::text),
  CONSTRAINT training_packages_pkey PRIMARY KEY (training_package_id),
  CONSTRAINT training_packages_source_set_digest_sha256_check CHECK (source_set_digest_sha256 IS NULL OR source_set_digest_sha256 ~ '^[0-9a-f]{64}$'::text),
  CONSTRAINT training_packages_status_check CHECK (status = ANY (ARRAY['DISCOVERED_UNBOUND'::text, 'REGISTERED'::text, 'QUALIFIED_BASE'::text, 'RETIRED'::text, 'SUPERSEDED'::text]))
);

CREATE TABLE bt2.training_qualifications (
  qualification_id uuid NOT NULL DEFAULT gen_random_uuid(),
  agent_key text NOT NULL,
  training_package_id uuid NOT NULL,
  outcome text NOT NULL,
  evaluator text,
  evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
  qualified_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT training_qualifications_agent_key_fkey FOREIGN KEY (agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT training_qualifications_outcome_check CHECK (outcome = ANY (ARRAY['PASS'::text, 'FAIL'::text, 'PENDING'::text, 'RETRACTED'::text, 'SUPERSEDED'::text])),
  CONSTRAINT training_qualifications_pkey PRIMARY KEY (qualification_id),
  CONSTRAINT training_qualifications_training_package_id_fkey FOREIGN KEY (training_package_id) REFERENCES bt2.training_packages(training_package_id)
);

CREATE TABLE bt2.operations (
  operation_id uuid NOT NULL,
  workspace_id uuid,
  actor_agent_key text,
  operation_kind text NOT NULL,
  target_locator text NOT NULL,
  idempotency_key text,
  request_digest_sha256 text NOT NULL,
  request_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  state text NOT NULL,
  attempted_at timestamp with time zone,
  resolved_at timestamp with time zone,
  result_digest_sha256 text,
  result_payload jsonb,
  do_not_repeat boolean NOT NULL DEFAULT false,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  updated_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT operations_actor_agent_key_fkey FOREIGN KEY (actor_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT operations_pkey PRIMARY KEY (operation_id),
  CONSTRAINT operations_request_digest_sha256_check CHECK (request_digest_sha256 ~ '^[0-9a-f]{64}$'::text),
  CONSTRAINT operations_result_digest_sha256_check CHECK (result_digest_sha256 IS NULL OR result_digest_sha256 ~ '^[0-9a-f]{64}$'::text),
  CONSTRAINT operations_state_check CHECK (state = ANY (ARRAY['PREPARED'::text, 'ATTEMPTED'::text, 'VERIFIED'::text, 'FAILED'::text, 'AMBIGUOUS'::text])),
  CONSTRAINT operations_target_locator_idempotency_key_key UNIQUE (target_locator, idempotency_key),
  CONSTRAINT operations_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES bt2.workspaces(workspace_id)
);

CREATE TABLE bt2.work_queue (
  queue_item_id uuid NOT NULL DEFAULT gen_random_uuid(),
  queue_name text NOT NULL DEFAULT 'agent_dispatch'::text,
  source_agent_key text,
  target_agent_key text,
  work_kind text NOT NULL,
  payload jsonb NOT NULL,
  payload_digest_sha256 text NOT NULL,
  state text NOT NULL DEFAULT 'READY'::text,
  priority integer NOT NULL DEFAULT 100,
  available_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  lease_token uuid,
  lease_owner text,
  lease_until timestamp with time zone,
  claim_count integer NOT NULL DEFAULT 0,
  last_error text,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  claimed_at timestamp with time zone,
  acked_at timestamp with time zone,
  CONSTRAINT work_queue_claim_count_check CHECK (claim_count >= 0),
  CONSTRAINT work_queue_payload_digest_sha256_check CHECK (payload_digest_sha256 ~ '^[0-9a-f]{64}$'::text),
  CONSTRAINT work_queue_pkey PRIMARY KEY (queue_item_id),
  CONSTRAINT work_queue_source_agent_key_fkey FOREIGN KEY (source_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT work_queue_state_check CHECK (state = ANY (ARRAY['READY'::text, 'CLAIMED'::text, 'ACKED'::text, 'DEAD'::text, 'CANCELLED'::text])),
  CONSTRAINT work_queue_target_agent_key_fkey FOREIGN KEY (target_agent_key) REFERENCES bt2.agents(agent_key)
);

CREATE TABLE bt2.bugs (
  bug_id uuid NOT NULL DEFAULT gen_random_uuid(),
  intake_key text NOT NULL,
  title text NOT NULL,
  description text NOT NULL DEFAULT ''::text,
  severity text NOT NULL,
  status text NOT NULL,
  component text,
  reported_by text,
  assigned_agent_key text,
  state_version bigint NOT NULL DEFAULT 1,
  evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  updated_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  closed_at timestamp with time zone,
  intake_digest_sha256 text,
  CONSTRAINT bugs_assigned_agent_key_fkey FOREIGN KEY (assigned_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT bugs_intake_digest_sha256_check CHECK (intake_digest_sha256 IS NULL OR intake_digest_sha256 ~ '^[0-9a-f]{64}$'::text),
  CONSTRAINT bugs_intake_key_key UNIQUE (intake_key),
  CONSTRAINT bugs_pkey PRIMARY KEY (bug_id),
  CONSTRAINT bugs_severity_check CHECK (severity = ANY (ARRAY['LOW'::text, 'MEDIUM'::text, 'HIGH'::text, 'CRITICAL'::text])),
  CONSTRAINT bugs_state_version_check CHECK (state_version > 0),
  CONSTRAINT bugs_status_check CHECK (status = ANY (ARRAY['NEW'::text, 'TRIAGED'::text, 'IN_PROGRESS'::text, 'BLOCKED'::text, 'FIXED'::text, 'VERIFYING'::text, 'CLOSED'::text, 'REOPENED'::text]))
);

CREATE TABLE bt2.bug_events (
  bug_event_id uuid NOT NULL DEFAULT gen_random_uuid(),
  bug_id uuid NOT NULL,
  state_version bigint NOT NULL,
  event_type text NOT NULL,
  actor_agent_key text,
  operation_id uuid,
  queue_item_id uuid,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT bug_events_actor_agent_key_fkey FOREIGN KEY (actor_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT bug_events_bug_id_fkey FOREIGN KEY (bug_id) REFERENCES bt2.bugs(bug_id),
  CONSTRAINT bug_events_bug_id_state_version_key UNIQUE (bug_id, state_version),
  CONSTRAINT bug_events_operation_id_fkey FOREIGN KEY (operation_id) REFERENCES bt2.operations(operation_id),
  CONSTRAINT bug_events_pkey PRIMARY KEY (bug_event_id),
  CONSTRAINT bug_events_queue_item_id_fkey FOREIGN KEY (queue_item_id) REFERENCES bt2.work_queue(queue_item_id)
);

CREATE TABLE bt2.workspace_checkpoints (
  workspace_checkpoint_id uuid NOT NULL DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL,
  predecessor_checkpoint_id uuid,
  generation bigint NOT NULL,
  payload jsonb NOT NULL,
  payload_digest_sha256 text NOT NULL,
  created_by_agent_key text,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT workspace_checkpoints_check CHECK (predecessor_checkpoint_id IS NULL OR predecessor_checkpoint_id <> workspace_checkpoint_id),
  CONSTRAINT workspace_checkpoints_created_by_agent_key_fkey FOREIGN KEY (created_by_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT workspace_checkpoints_generation_check CHECK (generation >= 0),
  CONSTRAINT workspace_checkpoints_payload_digest_sha256_check CHECK (payload_digest_sha256 ~ '^[0-9a-f]{64}$'::text),
  CONSTRAINT workspace_checkpoints_pkey PRIMARY KEY (workspace_checkpoint_id),
  CONSTRAINT workspace_checkpoints_predecessor_checkpoint_id_fkey FOREIGN KEY (predecessor_checkpoint_id) REFERENCES bt2.workspace_checkpoints(workspace_checkpoint_id),
  CONSTRAINT workspace_checkpoints_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES bt2.workspaces(workspace_id),
  CONSTRAINT workspace_checkpoints_workspace_id_generation_key UNIQUE (workspace_id, generation)
);

CREATE TABLE bt2.operational_checkpoints (
  checkpoint_id uuid NOT NULL DEFAULT gen_random_uuid(),
  agent_key text NOT NULL,
  predecessor_checkpoint_id uuid,
  training_package_id uuid,
  qualification_id uuid,
  checkpoint_schema text NOT NULL,
  payload jsonb NOT NULL,
  payload_digest_sha256 text NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT operational_checkpoints_agent_key_fkey FOREIGN KEY (agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT operational_checkpoints_check CHECK (predecessor_checkpoint_id IS NULL OR predecessor_checkpoint_id <> checkpoint_id),
  CONSTRAINT operational_checkpoints_payload_digest_sha256_check CHECK (payload_digest_sha256 ~ '^[0-9a-f]{64}$'::text),
  CONSTRAINT operational_checkpoints_pkey PRIMARY KEY (checkpoint_id),
  CONSTRAINT operational_checkpoints_predecessor_checkpoint_id_fkey FOREIGN KEY (predecessor_checkpoint_id) REFERENCES bt2.operational_checkpoints(checkpoint_id),
  CONSTRAINT operational_checkpoints_qualification_id_fkey FOREIGN KEY (qualification_id) REFERENCES bt2.training_qualifications(qualification_id),
  CONSTRAINT operational_checkpoints_training_package_id_fkey FOREIGN KEY (training_package_id) REFERENCES bt2.training_packages(training_package_id)
);

CREATE TABLE bt2.handoffs (
  handoff_id uuid NOT NULL DEFAULT gen_random_uuid(),
  workspace_id uuid,
  from_agent_key text,
  to_agent_key text,
  payload jsonb NOT NULL,
  payload_digest_sha256 text NOT NULL,
  status text NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  accepted_at timestamp with time zone,
  CONSTRAINT handoffs_from_agent_key_fkey FOREIGN KEY (from_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT handoffs_payload_digest_sha256_check CHECK (payload_digest_sha256 ~ '^[0-9a-f]{64}$'::text),
  CONSTRAINT handoffs_pkey PRIMARY KEY (handoff_id),
  CONSTRAINT handoffs_status_check CHECK (status = ANY (ARRAY['OPEN'::text, 'ACCEPTED'::text, 'SUPERSEDED'::text, 'CLOSED'::text])),
  CONSTRAINT handoffs_to_agent_key_fkey FOREIGN KEY (to_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT handoffs_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES bt2.workspaces(workspace_id)
);

CREATE TABLE bt2.decisions (
  decision_id uuid NOT NULL DEFAULT gen_random_uuid(),
  workspace_id uuid,
  decision_key text NOT NULL,
  decided_by_agent_key text,
  decision_payload jsonb NOT NULL,
  evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
  supersedes_decision_id uuid,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT decisions_decided_by_agent_key_fkey FOREIGN KEY (decided_by_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT decisions_pkey PRIMARY KEY (decision_id),
  CONSTRAINT decisions_supersedes_decision_id_fkey FOREIGN KEY (supersedes_decision_id) REFERENCES bt2.decisions(decision_id),
  CONSTRAINT decisions_workspace_id_decision_key_decision_id_key UNIQUE (workspace_id, decision_key, decision_id),
  CONSTRAINT decisions_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES bt2.workspaces(workspace_id)
);

CREATE TABLE bt2.assignments (
  assignment_id uuid NOT NULL DEFAULT gen_random_uuid(),
  assignment_key text NOT NULL,
  scope_kind text NOT NULL,
  scope_locator text NOT NULL,
  assigned_by text NOT NULL,
  assignee_agent_key text NOT NULL,
  status text NOT NULL,
  authority_class text NOT NULL DEFAULT 'ASSIGNED_WORK'::text,
  constraints jsonb NOT NULL DEFAULT '{}'::jsonb,
  source_provenance jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  updated_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT assignments_assignee_agent_key_fkey FOREIGN KEY (assignee_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT assignments_assignment_key_assignee_agent_key_status_key UNIQUE (assignment_key, assignee_agent_key, status),
  CONSTRAINT assignments_pkey PRIMARY KEY (assignment_id),
  CONSTRAINT assignments_status_check CHECK (status = ANY (ARRAY['ACTIVE'::text, 'PAUSED'::text, 'COMPLETED'::text, 'SUPERSEDED'::text, 'CANCELLED'::text]))
);

CREATE TABLE bt2.coordination_events (
  event_id uuid NOT NULL DEFAULT gen_random_uuid(),
  event_sequence bigint NOT NULL,
  operation_id text NOT NULL,
  request_digest text NOT NULL,
  thread_key text NOT NULL,
  source_agent_key text,
  target_agent_key text,
  source_address text,
  target_address text,
  event_type text NOT NULL,
  status text NOT NULL,
  objective text NOT NULL,
  summary text NOT NULL,
  active_issue text,
  supersedes_event_id uuid,
  acknowledges_event_id uuid,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  reference_data jsonb NOT NULL DEFAULT '{}'::jsonb,
  record_time timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT coordination_events_acknowledges_event_id_fkey FOREIGN KEY (acknowledges_event_id) REFERENCES bt2.coordination_events(event_id),
  CONSTRAINT coordination_events_event_sequence_key UNIQUE (event_sequence),
  CONSTRAINT coordination_events_pkey PRIMARY KEY (event_id),
  CONSTRAINT coordination_events_source_agent_key_fkey FOREIGN KEY (source_agent_key) REFERENCES bt2.agents(agent_key),
  CONSTRAINT coordination_events_supersedes_event_id_fkey FOREIGN KEY (supersedes_event_id) REFERENCES bt2.coordination_events(event_id),
  CONSTRAINT coordination_events_target_agent_key_fkey FOREIGN KEY (target_agent_key) REFERENCES bt2.agents(agent_key)
);

CREATE TABLE bt2.governance_notices (
  notice_id bigint NOT NULL,
  notice_key text NOT NULL,
  audience text NOT NULL,
  subject text NOT NULL,
  body jsonb NOT NULL,
  created_by text NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  invalidated_at timestamp with time zone,
  source_snapshot_id uuid,
  CONSTRAINT governance_notices_notice_key_key UNIQUE (notice_key),
  CONSTRAINT governance_notices_pkey PRIMARY KEY (notice_id),
  CONSTRAINT governance_notices_source_snapshot_id_fkey FOREIGN KEY (source_snapshot_id) REFERENCES bt2.source_snapshots(source_snapshot_id)
);

CREATE TABLE bt2.material_schema_policy (
  schema_version text NOT NULL,
  canonicalizer_digest text NOT NULL,
  semantic_projector_digest text NOT NULL,
  semantic_fields text[] NOT NULL,
  CONSTRAINT material_schema_policy_pkey PRIMARY KEY (schema_version),
  CONSTRAINT material_schema_policy_semantic_fields_check CHECK (cardinality(semantic_fields) > 0)
);

CREATE TABLE bt2.material_profiles (
  project_scope text NOT NULL,
  profile_digest text NOT NULL,
  predecessor_digest text,
  policy_digest text NOT NULL,
  accepted_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  accepted boolean NOT NULL DEFAULT true,
  CONSTRAINT material_profiles_check CHECK (predecessor_digest IS NULL OR predecessor_digest <> profile_digest),
  CONSTRAINT material_profiles_pkey PRIMARY KEY (project_scope, profile_digest)
);

CREATE TABLE bt2.material_producer_permits (
  permit_id uuid NOT NULL,
  project_scope text NOT NULL,
  producer_principal text NOT NULL,
  schema_version text NOT NULL,
  profile_digest text NOT NULL,
  policy_digest text NOT NULL,
  valid_from timestamp with time zone NOT NULL,
  valid_until timestamp with time zone NOT NULL,
  invalidated_at timestamp with time zone,
  CONSTRAINT material_producer_permits_permit_id_project_scope_producer__key UNIQUE (permit_id, project_scope, producer_principal, schema_version, profile_digest, policy_digest),
  CONSTRAINT material_producer_permits_pkey PRIMARY KEY (permit_id),
  CONSTRAINT material_producer_permits_project_scope_profile_digest_fkey FOREIGN KEY (project_scope, profile_digest) REFERENCES bt2.material_profiles(project_scope, profile_digest),
  CONSTRAINT material_producer_permits_schema_version_fkey FOREIGN KEY (schema_version) REFERENCES bt2.material_schema_policy(schema_version)
);

CREATE TABLE bt2.materials (
  material_id uuid NOT NULL,
  project_scope text NOT NULL,
  schema_version text NOT NULL,
  semantic_key text NOT NULL,
  canonical_digest text NOT NULL,
  source_digest text NOT NULL,
  canonical_payload jsonb NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT materials_pkey PRIMARY KEY (material_id),
  CONSTRAINT materials_project_scope_schema_version_semantic_key_key UNIQUE (project_scope, schema_version, semantic_key),
  CONSTRAINT materials_schema_version_fkey FOREIGN KEY (schema_version) REFERENCES bt2.material_schema_policy(schema_version)
);

CREATE TABLE bt2.material_receipts (
  receipt_id uuid NOT NULL,
  material_id uuid NOT NULL,
  project_scope text NOT NULL,
  producer_principal text NOT NULL,
  permit_id uuid NOT NULL,
  profile_digest text NOT NULL,
  policy_digest text NOT NULL,
  schema_version text NOT NULL,
  semantic_key text NOT NULL,
  canonical_digest text NOT NULL,
  source_digest text NOT NULL,
  admitted_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT material_receipts_material_id_fkey FOREIGN KEY (material_id) REFERENCES bt2.materials(material_id),
  CONSTRAINT material_receipts_material_id_key UNIQUE (material_id),
  CONSTRAINT material_receipts_permit_id_project_scope_producer_princip_fkey FOREIGN KEY (permit_id, project_scope, producer_principal, schema_version, profile_digest, policy_digest) REFERENCES bt2.material_producer_permits(permit_id, project_scope, producer_principal, schema_version, profile_digest, policy_digest),
  CONSTRAINT material_receipts_pkey PRIMARY KEY (receipt_id)
);

CREATE TABLE bt2.material_seed_receipts (
  source_collective_id text NOT NULL,
  source_event_id text NOT NULL,
  source_reducer_digest text NOT NULL,
  semantic_role text NOT NULL,
  imported_material_digest text NOT NULL,
  material_id uuid NOT NULL,
  imported_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT material_seed_receipts_material_id_fkey FOREIGN KEY (material_id) REFERENCES bt2.materials(material_id),
  CONSTRAINT material_seed_receipts_material_id_key UNIQUE (material_id),
  CONSTRAINT material_seed_receipts_pkey PRIMARY KEY (source_collective_id, source_event_id)
);

CREATE TABLE bt2.migration_receipts (
  migration_receipt_id uuid NOT NULL DEFAULT gen_random_uuid(),
  migration_key text NOT NULL,
  source_system text NOT NULL,
  source_snapshot_id uuid,
  target_component text NOT NULL,
  migration_digest_sha256 text NOT NULL,
  result_state text NOT NULL,
  evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
  applied_at timestamp with time zone,
  verified_at timestamp with time zone,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT migration_receipts_migration_digest_sha256_check CHECK (migration_digest_sha256 ~ '^[0-9a-f]{64}$'::text),
  CONSTRAINT migration_receipts_migration_key_key UNIQUE (migration_key),
  CONSTRAINT migration_receipts_pkey PRIMARY KEY (migration_receipt_id),
  CONSTRAINT migration_receipts_result_state_check CHECK (result_state = ANY (ARRAY['PREPARED'::text, 'APPLIED'::text, 'VERIFIED'::text, 'FAILED'::text, 'SUPERSEDED'::text])),
  CONSTRAINT migration_receipts_source_snapshot_id_fkey FOREIGN KEY (source_snapshot_id) REFERENCES bt2.source_snapshots(source_snapshot_id)
);

CREATE TABLE bt2.platform_meta (
  singleton boolean NOT NULL DEFAULT true,
  platform_name text NOT NULL,
  schema_version text NOT NULL,
  backend_kind text NOT NULL,
  backend_locator text NOT NULL,
  source_manifest jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  updated_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT platform_meta_pkey PRIMARY KEY (singleton),
  CONSTRAINT platform_meta_singleton_check CHECK (singleton)
);

CREATE TABLE bt2_legacy.source_objects (
  source_object_id uuid NOT NULL DEFAULT gen_random_uuid(),
  source_system text NOT NULL,
  object_kind text NOT NULL,
  qualified_name text NOT NULL,
  source_ref text,
  definition_text text,
  definition_digest_sha256 text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  source_snapshot_id uuid,
  captured_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT source_objects_definition_digest_sha256_check CHECK (definition_digest_sha256 IS NULL OR definition_digest_sha256 ~ '^[0-9a-f]{64}$'::text),
  CONSTRAINT source_objects_pkey PRIMARY KEY (source_object_id),
  CONSTRAINT source_objects_source_snapshot_id_fkey FOREIGN KEY (source_snapshot_id) REFERENCES bt2.source_snapshots(source_snapshot_id),
  CONSTRAINT source_objects_source_system_object_kind_qualified_name_sou_key UNIQUE (source_system, object_kind, qualified_name, source_ref)
);

CREATE TABLE bt2_legacy.source_rows (
  source_row_id uuid NOT NULL DEFAULT gen_random_uuid(),
  source_system text NOT NULL,
  source_schema text NOT NULL,
  source_relation text NOT NULL,
  source_primary_key text NOT NULL,
  row_data jsonb NOT NULL,
  source_snapshot_id uuid,
  captured_at timestamp with time zone NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT source_rows_pkey PRIMARY KEY (source_row_id),
  CONSTRAINT source_rows_source_snapshot_id_fkey FOREIGN KEY (source_snapshot_id) REFERENCES bt2.source_snapshots(source_snapshot_id),
  CONSTRAINT source_rows_source_system_source_schema_source_relation_sou_key UNIQUE (source_system, source_schema, source_relation, source_primary_key)
);
