-- BT2 training preservation SHA-256 claim hostile regression V1.
-- Proves BYTE_PRESERVED_VERIFIED digest claims cannot drift independently of
-- their source-controlled preservation subject. Entire test rolls back.

BEGIN;

INSERT INTO bt2.agent_units(unit_key,display_name,unit_type,orchestrator_agent_key)
VALUES ('digest_guard_test','digest guard test','ORCHESTRATED_TEAM','five');

INSERT INTO bt2.agents(agent_key,display_name,numerical_identity,unit_key,role_kind,role_summary)
VALUES ('five','Five',5,'digest_guard_test','PRIMARY','digest guard test');

INSERT INTO bt2.migration_receipts(
  migration_key,source_system,target_component,migration_digest_sha256,
  result_state,evidence,applied_at,verified_at
) VALUES (
  'BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1',
  'CI_PRESERVATION',
  'training-source-registry',
  encode(
    public.digest(
      convert_to('BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1','UTF8'),
      'sha256'
    ),
    'hex'
  ),
  'VERIFIED',
  jsonb_build_object(
    'source_package_tree','f6c962e81c75deab3aa55d300fc4f9f9fa89f034',
    'target_package_tree','f6c962e81c75deab3aa55d300fc4f9f9fa89f034',
    'manifest_digest_sha256','164ee92a70f6585dece59dca09ab84bd6020a4d950393b127091aed91713687c',
    'source_set_digest_sha256','80d2aab944ee8c8e13b83ae99aacc4ba530bc42cda69ed6c9ab21958a64e55f8',
    'qualification_effect','NONE',
    'runtime_installation_effect','NONE',
    'authority_effect','NONE'
  ),
  clock_timestamp(),clock_timestamp()
);

SELECT bt2.register_preserved_training_package_v1(
  'five','1.0.0','thebrazenbeard/build-team-2.0','main',
  'da419ea83323c54908380c6ad57d65ea2c580f14',
  '912f329cf1f780171827a64b7bc8ce65512a1efa',
  'training/roles/five/v1.0.0',
  'archive/training-sources/build-team-2.0/five/v1.0.0/manifest.yaml',
  'f6c962e81c75deab3aa55d300fc4f9f9fa89f034',
  '124db5b0aca892f05506d0a7086c8d9a2c9cd83f',
  'BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1',
  '164ee92a70f6585dece59dca09ab84bd6020a4d950393b127091aed91713687c',
  '80d2aab944ee8c8e13b83ae99aacc4ba530bc42cda69ed6c9ab21958a64e55f8'
);

DO $test$
DECLARE
  v_id uuid;
BEGIN
  SELECT training_package_id
  INTO STRICT v_id
  FROM bt2.training_packages
  WHERE agent_key='five'
    AND version='1.0.0'
    AND package_tree_git_sha1='f6c962e81c75deab3aa55d300fc4f9f9fa89f034';

  IF (
    SELECT manifest_digest_sha256
    FROM bt2.training_preservation_digest_bindings_v1
    WHERE preservation_migration_key='BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1'
  ) IS DISTINCT FROM
    '164ee92a70f6585dece59dca09ab84bd6020a4d950393b127091aed91713687c'
  THEN
    RAISE EXCEPTION 'MANIFEST_DIGEST_BINDING_NOT_RECONSTRUCTED';
  END IF;

  IF (
    SELECT source_set_digest_sha256
    FROM bt2.training_preservation_digest_bindings_v1
    WHERE preservation_migration_key='BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1'
  ) IS DISTINCT FROM
    '80d2aab944ee8c8e13b83ae99aacc4ba530bc42cda69ed6c9ab21958a64e55f8'
  THEN
    RAISE EXCEPTION 'SOURCE_SET_DIGEST_BINDING_NOT_RECONSTRUCTED';
  END IF;

  BEGIN
    UPDATE bt2.training_packages
    SET manifest_digest_sha256=repeat('f',64)
    WHERE training_package_id=v_id;
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:manifest_digest_sha256';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:manifest_digest_sha256' THEN RAISE; END IF;
    IF SQLERRM IS DISTINCT FROM
       'PRESERVATION_PROVENANCE_MISMATCH:manifest_digest_sha256' THEN
      RAISE;
    END IF;
  END;

  BEGIN
    UPDATE bt2.training_packages
    SET source_set_digest_sha256=repeat('e',64)
    WHERE training_package_id=v_id;
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:source_set_digest_sha256';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:source_set_digest_sha256' THEN RAISE; END IF;
    IF SQLERRM IS DISTINCT FROM
       'PRESERVATION_PROVENANCE_MISMATCH:source_set_digest_sha256' THEN
      RAISE;
    END IF;
  END;

  BEGIN
    UPDATE bt2.training_preservation_digest_bindings_v1
    SET source_set_digest_sha256=repeat('d',64)
    WHERE preservation_migration_key='BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1';
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:digest_binding_mutation';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:digest_binding_mutation' THEN RAISE; END IF;
    IF SQLERRM IS DISTINCT FROM
       'TRAINING_PRESERVATION_PROVENANCE_BINDINGS_ARE_IMMUTABLE' THEN
      RAISE;
    END IF;
  END;
END
$test$;

DO $null_subject$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM bt2.training_preservation_digest_bindings_v1
    WHERE preservation_migration_key='BT2-TRAINING-ONE-V1.0.0-BYTE-PRESERVATION-V1'
      AND (manifest_digest_sha256 IS NOT NULL OR source_set_digest_sha256 IS NOT NULL)
  ) THEN
    RAISE EXCEPTION 'UNESTABLISHED_DIGEST_CLAIM_WAS_FABRICATED';
  END IF;
END
$null_subject$;

ROLLBACK;
