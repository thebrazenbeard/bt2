-- BT2 training preservation SHA-256 claim binding V1.
-- Forward-only supplement to 0022.
--
-- 0022 binds preserved-package Git provenance. This migration closes the remaining
-- claim-integrity gap for manifest_digest_sha256 and source_set_digest_sha256.
-- It does not weaken or rewrite 0022 and does not establish compatibility,
-- qualification, installation, activation, assignment, authority, or currentness.

CREATE TABLE bt2.training_preservation_digest_bindings_v1 (
  preservation_migration_key text PRIMARY KEY
    REFERENCES bt2.training_preservation_provenance_bindings_v1(preservation_migration_key),
  manifest_digest_sha256 text,
  source_set_digest_sha256 text,
  evidence_class text NOT NULL DEFAULT
    'SOURCE_CONTROLLED_RECONCILED_PRESERVATION_DIGEST_CLAIMS_V1',
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT training_preservation_digest_binding_manifest_check
    CHECK (
      manifest_digest_sha256 IS NULL
      OR manifest_digest_sha256 ~ '^[0-9a-f]{64}$'
    ),
  CONSTRAINT training_preservation_digest_binding_source_set_check
    CHECK (
      source_set_digest_sha256 IS NULL
      OR source_set_digest_sha256 ~ '^[0-9a-f]{64}$'
    )
);

INSERT INTO bt2.training_preservation_digest_bindings_v1(
  preservation_migration_key,manifest_digest_sha256,source_set_digest_sha256
) VALUES
  ('BT2-TRAINING-ONE-V1.0.0-BYTE-PRESERVATION-V1',NULL,NULL),
  ('BT2-TRAINING-TWO-V1.0.0-BYTE-PRESERVATION-V1',NULL,NULL),
  ('BT2-TRAINING-THREE-V1.0.0-BYTE-PRESERVATION-V1',NULL,NULL),
  ('BT2-TRAINING-SEVEN-V1.0.0-BYTE-PRESERVATION-V1',NULL,NULL),
  ('BT2-TRAINING-EIGHT-V1.0.0-BYTE-PRESERVATION-V1',NULL,NULL),
  ('BT2-TRAINING-MASA-V1.0.0-BYTE-PRESERVATION-V1',NULL,NULL),
  ('BT2-TRAINING-MUNE-V1.0.1-BYTE-PRESERVATION-V1',NULL,NULL),
  ('BT2-TRAINING-HEPHAESTUS-V1.0.0-BYTE-PRESERVATION-V1',NULL,NULL),
  (
    'BT2-TRAINING-FOUR-V1.0.1-BYTE-PRESERVATION-V1',
    NULL,
    '1070866d342043c21d06d9bc384fbf7cf78d231850ef2edef514b3e95229c332'
  ),
  (
    'BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1',
    '164ee92a70f6585dece59dca09ab84bd6020a4d950393b127091aed91713687c',
    '80d2aab944ee8c8e13b83ae99aacc4ba530bc42cda69ed6c9ab21958a64e55f8'
  ),
  (
    'BT2-TRAINING-SIX-V1.0.0-BYTE-PRESERVATION-V1',
    '32ed842c8bb6c2ccc49bb327189da9b03178b403f05ad6b10cca9b5f1ceeff38',
    'ef44176582819750193c7d591e9ee449ea8c3d6743a8bff3eb5228baf4fad1cc'
  ),
  (
    'BT2-TRAINING-NINE-V1.0.0-BYTE-PRESERVATION-V1',
    'a0702c71cd14521cf88312ee9f07c6bf5ccb5a95079b047332e33a532f32e67b',
    'bcbee02e5e7f59b763ba1a441a66c4e3b83210befcb85ab7f66a5d0ccf7769e7'
  ),
  (
    'BT2-TRAINING-THIRTEEN-V1.0.0-BYTE-PRESERVATION-V1',
    '49ca83e55940caecf6df56170bcd5ddca8044933d56db897fbfe0f052c87fc3e',
    '89f3da76b9033c9302e2ddb85c68b6bf0b7856383d7bce65f671170d4a8a7bc1'
  );

CREATE TRIGGER training_preservation_digest_bindings_no_update_delete_v1
BEFORE UPDATE OR DELETE ON bt2.training_preservation_digest_bindings_v1
FOR EACH ROW EXECUTE FUNCTION bt2.reject_training_preservation_binding_mutation_v1();

REVOKE INSERT,UPDATE,DELETE,TRUNCATE
ON bt2.training_preservation_digest_bindings_v1
FROM PUBLIC;

CREATE OR REPLACE FUNCTION bt2.guard_training_package_preservation_digest_binding_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
DECLARE
  v_receipt record;
  v_binding bt2.training_preservation_digest_bindings_v1%ROWTYPE;
BEGIN
  IF NEW.source_binding_state = 'BYTE_PRESERVED_VERIFIED' THEN
    IF NEW.preservation_receipt_id IS NULL THEN
      RAISE EXCEPTION 'BYTE_PRESERVATION_REQUIRES_RECEIPT';
    END IF;

    SELECT mr.migration_key,mr.evidence
    INTO STRICT v_receipt
    FROM bt2.migration_receipts mr
    WHERE mr.migration_receipt_id=NEW.preservation_receipt_id;

    SELECT b.*
    INTO STRICT v_binding
    FROM bt2.training_preservation_digest_bindings_v1 b
    WHERE b.preservation_migration_key=v_receipt.migration_key;

    IF NEW.manifest_digest_sha256 IS DISTINCT FROM v_binding.manifest_digest_sha256 THEN
      RAISE EXCEPTION 'PRESERVATION_PROVENANCE_MISMATCH:manifest_digest_sha256';
    END IF;

    IF NEW.source_set_digest_sha256 IS DISTINCT FROM v_binding.source_set_digest_sha256 THEN
      RAISE EXCEPTION 'PRESERVATION_PROVENANCE_MISMATCH:source_set_digest_sha256';
    END IF;

    IF v_receipt.evidence ? 'manifest_digest_sha256'
       AND v_receipt.evidence->>'manifest_digest_sha256'
           IS DISTINCT FROM v_binding.manifest_digest_sha256 THEN
      RAISE EXCEPTION
        'PRESERVATION_RECEIPT_PROVENANCE_CONTRADICTION:manifest_digest_sha256';
    END IF;

    IF v_receipt.evidence ? 'source_set_digest_sha256'
       AND v_receipt.evidence->>'source_set_digest_sha256'
           IS DISTINCT FROM v_binding.source_set_digest_sha256 THEN
      RAISE EXCEPTION
        'PRESERVATION_RECEIPT_PROVENANCE_CONTRADICTION:source_set_digest_sha256';
    END IF;
  END IF;

  RETURN NEW;
END
$function$;

CREATE TRIGGER training_packages_preservation_digest_guard_v1
BEFORE INSERT OR UPDATE OF
  manifest_digest_sha256,source_set_digest_sha256,
  preservation_receipt_id,source_binding_state
ON bt2.training_packages
FOR EACH ROW EXECUTE FUNCTION bt2.guard_training_package_preservation_digest_binding_v1();

-- Fail closed on a live upgrade if a pre-existing BYTE_PRESERVED_VERIFIED row
-- disagrees with either the 0022 Git-provenance binding or the digest binding.
DO $validate_existing$
DECLARE
  v_bad uuid;
BEGIN
  SELECT tp.training_package_id
  INTO v_bad
  FROM bt2.training_packages tp
  LEFT JOIN bt2.migration_receipts mr
    ON mr.migration_receipt_id=tp.preservation_receipt_id
  LEFT JOIN bt2.training_preservation_provenance_bindings_v1 pb
    ON pb.preservation_migration_key=mr.migration_key
  LEFT JOIN bt2.training_preservation_digest_bindings_v1 db
    ON db.preservation_migration_key=mr.migration_key
  WHERE tp.source_binding_state='BYTE_PRESERVED_VERIFIED'
    AND (
      mr.migration_receipt_id IS NULL
      OR mr.result_state <> 'VERIFIED'
      OR pb.preservation_migration_key IS NULL
      OR db.preservation_migration_key IS NULL
      OR lower(
           COALESCE(
             mr.evidence->>'target_package_tree',
             mr.evidence->>'source_package_tree'
           )
         ) IS DISTINCT FROM lower(pb.package_tree_git_sha1)
      OR mr.evidence->>'qualification_effect' IS DISTINCT FROM 'NONE'
      OR mr.evidence->>'runtime_installation_effect' IS DISTINCT FROM 'NONE'
      OR tp.agent_key IS DISTINCT FROM pb.agent_key
      OR tp.version IS DISTINCT FROM pb.version
      OR tp.source_repository IS DISTINCT FROM pb.source_repository
      OR tp.source_ref IS DISTINCT FROM pb.source_ref
      OR tp.source_commit IS DISTINCT FROM pb.source_commit
      OR tp.source_tree IS DISTINCT FROM pb.source_tree
      OR tp.source_package_path IS DISTINCT FROM pb.source_package_path
      OR tp.manifest_path IS DISTINCT FROM pb.target_manifest_path
      OR lower(tp.package_tree_git_sha1) IS DISTINCT FROM lower(pb.package_tree_git_sha1)
      OR lower(tp.manifest_blob_git_sha1) IS DISTINCT FROM lower(pb.manifest_blob_git_sha1)
      OR tp.manifest_digest_sha256 IS DISTINCT FROM db.manifest_digest_sha256
      OR tp.source_set_digest_sha256 IS DISTINCT FROM db.source_set_digest_sha256
      OR (
        mr.evidence ? 'agent_key'
        AND mr.evidence->>'agent_key' IS DISTINCT FROM pb.agent_key
      )
      OR (
        mr.evidence ? 'training_version'
        AND mr.evidence->>'training_version' IS DISTINCT FROM pb.version
      )
      OR (
        mr.evidence ? 'source_ref'
        AND mr.evidence->>'source_ref' IS DISTINCT FROM pb.source_ref
      )
      OR (
        mr.evidence ? 'source_commit'
        AND mr.evidence->>'source_commit' IS DISTINCT FROM pb.source_commit
      )
      OR (
        mr.evidence ? 'source_commit_tree'
        AND mr.evidence->>'source_commit_tree' IS DISTINCT FROM pb.source_tree
      )
      OR (
        mr.evidence ? 'source_package_path'
        AND mr.evidence->>'source_package_path' IS DISTINCT FROM pb.source_package_path
      )
      OR (
        mr.evidence ? 'manifest_blob'
        AND lower(mr.evidence->>'manifest_blob')
            IS DISTINCT FROM lower(pb.manifest_blob_git_sha1)
      )
      OR (
        mr.evidence ? 'manifest_digest_sha256'
        AND mr.evidence->>'manifest_digest_sha256'
            IS DISTINCT FROM db.manifest_digest_sha256
      )
      OR (
        mr.evidence ? 'source_set_digest_sha256'
        AND mr.evidence->>'source_set_digest_sha256'
            IS DISTINCT FROM db.source_set_digest_sha256
      )
    )
  LIMIT 1;

  IF v_bad IS NOT NULL THEN
    RAISE EXCEPTION 'EXISTING_BYTE_PRESERVED_PROVENANCE_MISMATCH:%',v_bad;
  END IF;
END
$validate_existing$;
