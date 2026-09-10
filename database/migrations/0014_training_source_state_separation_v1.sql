-- BT2 training source-state separation V1.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.
-- Purpose: keep package/source preservation distinct from compatibility,
-- qualification, runtime installation, assignment, and authority.

ALTER TABLE bt2.training_packages
  ADD COLUMN source_binding_state text NOT NULL DEFAULT 'DISCOVERED',
  ADD COLUMN compatibility_state text NOT NULL DEFAULT 'UNASSESSED',
  ADD COLUMN source_package_path text,
  ADD COLUMN package_tree_git_sha1 text,
  ADD COLUMN manifest_blob_git_sha1 text,
  ADD COLUMN preservation_receipt_id uuid,
  ADD COLUMN source_binding_verified_at timestamptz;

ALTER TABLE bt2.training_packages
  ADD CONSTRAINT training_packages_source_binding_state_check
  CHECK (source_binding_state IN ('DISCOVERED','SOURCE_BOUND','BYTE_PRESERVED_VERIFIED')),
  ADD CONSTRAINT training_packages_compatibility_state_check
  CHECK (compatibility_state IN ('UNASSESSED','COMPATIBLE','INCOMPATIBLE','SUPERSEDED')),
  ADD CONSTRAINT training_packages_package_tree_git_sha1_check
  CHECK (package_tree_git_sha1 IS NULL OR package_tree_git_sha1 ~ '^[0-9a-f]{40}$'),
  ADD CONSTRAINT training_packages_manifest_blob_git_sha1_check
  CHECK (manifest_blob_git_sha1 IS NULL OR manifest_blob_git_sha1 ~ '^[0-9a-f]{40}$'),
  ADD CONSTRAINT training_packages_verified_binding_shape_check
  CHECK (
    source_binding_state <> 'BYTE_PRESERVED_VERIFIED'
    OR (
      preservation_receipt_id IS NOT NULL
      AND package_tree_git_sha1 IS NOT NULL
      AND source_binding_verified_at IS NOT NULL
    )
  ),
  ADD CONSTRAINT training_packages_qualified_base_requires_compatibility_check
  CHECK (status <> 'QUALIFIED_BASE' OR compatibility_state = 'COMPATIBLE'),
  ADD CONSTRAINT training_packages_preservation_receipt_id_fkey
  FOREIGN KEY (preservation_receipt_id)
  REFERENCES bt2.migration_receipts(migration_receipt_id);

CREATE UNIQUE INDEX training_packages_exact_package_tree_uniq
  ON bt2.training_packages(agent_key,version,package_tree_git_sha1)
  WHERE package_tree_git_sha1 IS NOT NULL;

CREATE OR REPLACE FUNCTION bt2.guard_training_package_source_binding_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
DECLARE
  v_receipt record;
  v_receipt_tree text;
BEGIN
  IF NEW.source_binding_state = 'BYTE_PRESERVED_VERIFIED' THEN
    IF NEW.preservation_receipt_id IS NULL THEN
      RAISE EXCEPTION 'BYTE_PRESERVATION_REQUIRES_RECEIPT';
    END IF;

    SELECT mr.result_state,mr.evidence
    INTO STRICT v_receipt
    FROM bt2.migration_receipts mr
    WHERE mr.migration_receipt_id=NEW.preservation_receipt_id;

    IF v_receipt.result_state <> 'VERIFIED' THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_NOT_VERIFIED';
    END IF;

    v_receipt_tree:=COALESCE(
      v_receipt.evidence->>'target_package_tree',
      v_receipt.evidence->>'source_package_tree'
    );

    IF v_receipt_tree IS NULL
       OR lower(v_receipt_tree) IS DISTINCT FROM lower(NEW.package_tree_git_sha1) THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_PACKAGE_TREE_MISMATCH';
    END IF;

    IF v_receipt.evidence->>'qualification_effect' IS DISTINCT FROM 'NONE' THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_QUALIFICATION_EFFECT_NOT_NONE';
    END IF;

    IF v_receipt.evidence->>'runtime_installation_effect' IS DISTINCT FROM 'NONE' THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_RUNTIME_EFFECT_NOT_NONE';
    END IF;
  END IF;

  RETURN NEW;
END
$function$;

CREATE TRIGGER training_packages_source_binding_guard_v1
BEFORE INSERT OR UPDATE OF source_binding_state,preservation_receipt_id,package_tree_git_sha1
ON bt2.training_packages
FOR EACH ROW EXECUTE FUNCTION bt2.guard_training_package_source_binding_v1();

CREATE OR REPLACE FUNCTION bt2.guard_training_package_qualified_base_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
BEGIN
  IF NEW.status='QUALIFIED_BASE'
     AND (
       NEW.compatibility_state <> 'COMPATIBLE'
       OR NOT EXISTS (
         SELECT 1
         FROM bt2.training_qualifications tq
         WHERE tq.training_package_id=NEW.training_package_id
           AND tq.agent_key=NEW.agent_key
           AND tq.outcome='PASS'
       )
     ) THEN
    RAISE EXCEPTION 'QUALIFIED_BASE_REQUIRES_COMPATIBLE_PASS_EVIDENCE';
  END IF;
  RETURN NEW;
END
$function$;

CREATE TRIGGER training_packages_qualified_base_guard_v1
BEFORE INSERT OR UPDATE OF status,compatibility_state
ON bt2.training_packages
FOR EACH ROW EXECUTE FUNCTION bt2.guard_training_package_qualified_base_v1();

CREATE OR REPLACE FUNCTION bt2.register_preserved_training_package_v1(
  p_agent_key text,
  p_version text,
  p_source_repository text,
  p_source_ref text,
  p_source_commit text,
  p_source_tree text,
  p_source_package_path text,
  p_target_manifest_path text,
  p_package_tree_git_sha1 text,
  p_manifest_blob_git_sha1 text,
  p_preservation_migration_key text,
  p_manifest_digest_sha256 text DEFAULT NULL,
  p_source_set_digest_sha256 text DEFAULT NULL
) RETURNS uuid
LANGUAGE plpgsql
AS $function$
DECLARE
  v_receipt_id uuid;
  v_package_id uuid;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM bt2.agents a WHERE a.agent_key=p_agent_key) THEN
    RAISE EXCEPTION 'UNKNOWN_TRAINING_AGENT';
  END IF;
  IF p_version IS NULL OR btrim(p_version)='' THEN
    RAISE EXCEPTION 'INVALID_TRAINING_VERSION';
  END IF;
  IF p_package_tree_git_sha1 IS NULL
     OR p_package_tree_git_sha1 !~ '^[0-9a-f]{40}$' THEN
    RAISE EXCEPTION 'INVALID_PACKAGE_TREE_GIT_SHA1';
  END IF;

  SELECT mr.migration_receipt_id
  INTO STRICT v_receipt_id
  FROM bt2.migration_receipts mr
  WHERE mr.migration_key=p_preservation_migration_key
    AND mr.result_state='VERIFIED';

  INSERT INTO bt2.training_packages(
    training_package_id,agent_key,version,status,
    source_repository,source_ref,source_commit,source_tree,
    manifest_path,manifest_digest_sha256,source_set_digest_sha256,
    source_binding_state,compatibility_state,source_package_path,
    package_tree_git_sha1,manifest_blob_git_sha1,
    preservation_receipt_id,source_binding_verified_at,metadata
  ) VALUES(
    gen_random_uuid(),p_agent_key,p_version,'REGISTERED',
    p_source_repository,p_source_ref,p_source_commit,p_source_tree,
    p_target_manifest_path,p_manifest_digest_sha256,p_source_set_digest_sha256,
    'BYTE_PRESERVED_VERIFIED','UNASSESSED',p_source_package_path,
    lower(p_package_tree_git_sha1),lower(p_manifest_blob_git_sha1),
    v_receipt_id,clock_timestamp(),
    jsonb_build_object(
      'registration_basis','VERIFIED_BYTE_PRESERVATION_RECEIPT',
      'qualification_effect','NONE',
      'runtime_installation_effect','NONE',
      'authority_effect','NONE'
    )
  )
  ON CONFLICT (agent_key,version,package_tree_git_sha1)
    WHERE package_tree_git_sha1 IS NOT NULL
  DO UPDATE SET
    source_repository=EXCLUDED.source_repository,
    source_ref=EXCLUDED.source_ref,
    source_commit=EXCLUDED.source_commit,
    source_tree=EXCLUDED.source_tree,
    source_package_path=EXCLUDED.source_package_path,
    manifest_path=EXCLUDED.manifest_path,
    manifest_blob_git_sha1=EXCLUDED.manifest_blob_git_sha1,
    preservation_receipt_id=EXCLUDED.preservation_receipt_id,
    source_binding_state='BYTE_PRESERVED_VERIFIED',
    source_binding_verified_at=EXCLUDED.source_binding_verified_at,
    updated_at=clock_timestamp()
  RETURNING training_package_id INTO v_package_id;

  RETURN v_package_id;
END
$function$;
