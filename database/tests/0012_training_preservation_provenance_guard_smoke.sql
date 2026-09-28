-- BT2 training preservation provenance hostile regression V1.
-- Proves a VERIFIED same-tree preservation receipt cannot be reused to rewrite
-- authoritative training-package provenance. Entire test rolls back.

BEGIN;

INSERT INTO bt2.agent_units(unit_key,display_name,unit_type,orchestrator_agent_key)
VALUES ('provenance_guard_test','provenance guard test','ORCHESTRATED_TEAM','one');

INSERT INTO bt2.agents(agent_key,display_name,numerical_identity,unit_key,role_kind,role_summary)
VALUES ('one','One',1,'provenance_guard_test','PRIMARY','provenance guard test');

INSERT INTO bt2.migration_receipts(
  migration_key,source_system,target_component,migration_digest_sha256,
  result_state,evidence,applied_at,verified_at
) VALUES (
  'BT2-TRAINING-ONE-V1.0.0-BYTE-PRESERVATION-V1',
  'CI_PRESERVATION',
  'training-source-registry',
  encode(public.digest(convert_to('BT2-TRAINING-ONE-V1.0.0-BYTE-PRESERVATION-V1','UTF8'),'sha256'),'hex'),
  'VERIFIED',
  jsonb_build_object(
    'source_package_tree','e27ce67b67159fb445347ae9a8888fe3c480cdd1',
    'target_package_tree','e27ce67b67159fb445347ae9a8888fe3c480cdd1',
    'qualification_effect','NONE',
    'runtime_installation_effect','NONE',
    'authority_effect','NONE'
  ),
  clock_timestamp(),clock_timestamp()
);

SELECT bt2.register_preserved_training_package_v1(
  'one','1.0.0','thebrazenbeard/build-team-2.0','training/one-role-v1.0.0',
  'ed1f2c5515425deab4c77c2f4fd291a1086191d4','0cd6bca8a3d1aaab9e47f3f8b23d3a18a6f4d40a',
  'training/roles/one/v1.0.0',
  'archive/training-sources/build-team-2.0/one/v1.0.0/TRAINING_MANIFEST.yaml',
  'e27ce67b67159fb445347ae9a8888fe3c480cdd1','e6d8e6b4a8139d8073b08fe7f346107f66a16458',
  'BT2-TRAINING-ONE-V1.0.0-BYTE-PRESERVATION-V1'
);

DO $test$
DECLARE
  v_id uuid;
  v_original_digest text;
  v_recomputed_digest text;
BEGIN
  SELECT training_package_id
  INTO STRICT v_id
  FROM bt2.training_packages
  WHERE agent_key='one'
    AND version='1.0.0'
    AND package_tree_git_sha1='e27ce67b67159fb445347ae9a8888fe3c480cdd1';

  SELECT provenance_digest_sha256
  INTO STRICT v_original_digest
  FROM bt2.training_preservation_provenance_bindings_v1
  WHERE preservation_migration_key='BT2-TRAINING-ONE-V1.0.0-BYTE-PRESERVATION-V1';

  SELECT bt2.training_preservation_provenance_digest_v1(
    agent_key,version,source_repository,source_ref,source_commit,source_tree,
    source_package_path,target_manifest_path,package_tree_git_sha1,manifest_blob_git_sha1
  )
  INTO STRICT v_recomputed_digest
  FROM bt2.training_preservation_provenance_bindings_v1
  WHERE preservation_migration_key='BT2-TRAINING-ONE-V1.0.0-BYTE-PRESERVATION-V1';

  IF v_original_digest IS DISTINCT FROM v_recomputed_digest THEN
    RAISE EXCEPTION 'PROVENANCE_BINDING_DIGEST_NOT_REPRODUCIBLE';
  END IF;

  BEGIN
    UPDATE bt2.training_packages SET source_repository='thebrazenbeard/other' WHERE training_package_id=v_id;
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:source_repository';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:source_repository' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE 'PRESERVATION_PROVENANCE_MISMATCH:%' THEN RAISE; END IF;
  END;

  BEGIN
    UPDATE bt2.training_packages SET source_ref='main' WHERE training_package_id=v_id;
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:source_ref';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:source_ref' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE 'PRESERVATION_PROVENANCE_MISMATCH:%' THEN RAISE; END IF;
  END;

  BEGIN
    UPDATE bt2.training_packages SET source_commit='1111111111111111111111111111111111111111' WHERE training_package_id=v_id;
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:source_commit';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:source_commit' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE 'PRESERVATION_PROVENANCE_MISMATCH:%' THEN RAISE; END IF;
  END;

  BEGIN
    UPDATE bt2.training_packages SET source_tree='2222222222222222222222222222222222222222' WHERE training_package_id=v_id;
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:source_tree';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:source_tree' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE 'PRESERVATION_PROVENANCE_MISMATCH:%' THEN RAISE; END IF;
  END;

  BEGIN
    UPDATE bt2.training_packages SET agent_key='not-one' WHERE training_package_id=v_id;
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:agent_key';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:agent_key' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE 'PRESERVATION_PROVENANCE_MISMATCH:%' THEN RAISE; END IF;
  END;

  BEGIN
    UPDATE bt2.training_packages SET version='9.9.9' WHERE training_package_id=v_id;
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:version';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:version' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE 'PRESERVATION_PROVENANCE_MISMATCH:%' THEN RAISE; END IF;
  END;

  BEGIN
    UPDATE bt2.training_packages SET source_package_path='training/roles/one/other' WHERE training_package_id=v_id;
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:source_package_path';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:source_package_path' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE 'PRESERVATION_PROVENANCE_MISMATCH:%' THEN RAISE; END IF;
  END;

  BEGIN
    UPDATE bt2.training_packages SET manifest_path='archive/training-sources/other/manifest.yaml' WHERE training_package_id=v_id;
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:manifest_path';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:manifest_path' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE 'PRESERVATION_PROVENANCE_MISMATCH:%' THEN RAISE; END IF;
  END;

  BEGIN
    UPDATE bt2.training_packages SET manifest_blob_git_sha1='3333333333333333333333333333333333333333' WHERE training_package_id=v_id;
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:manifest_blob_git_sha1';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:manifest_blob_git_sha1' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE 'PRESERVATION_PROVENANCE_MISMATCH:%' THEN RAISE; END IF;
  END;

  BEGIN
    UPDATE bt2.training_preservation_provenance_bindings_v1
    SET source_ref='main'
    WHERE preservation_migration_key='BT2-TRAINING-ONE-V1.0.0-BYTE-PRESERVATION-V1';
    RAISE EXCEPTION 'HOSTILE_ACCEPTED:binding_mutation';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='HOSTILE_ACCEPTED:binding_mutation' THEN RAISE; END IF;
    IF SQLERRM IS DISTINCT FROM 'TRAINING_PRESERVATION_PROVENANCE_BINDINGS_ARE_IMMUTABLE' THEN RAISE; END IF;
  END;
END
$test$;

DO $effects$
BEGIN
  IF (SELECT count(*) FROM bt2.training_qualifications)<>0 THEN
    RAISE EXCEPTION 'PROVENANCE_GUARD_CREATED_QUALIFICATION';
  END IF;

  IF (SELECT count(*) FROM bt2.training_installation_events)<>0 THEN
    RAISE EXCEPTION 'PROVENANCE_GUARD_CREATED_INSTALLATION_EVENT';
  END IF;
END
$effects$;

ROLLBACK;
