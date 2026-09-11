-- Registry frontier receipt V3: eight-package base plus Four v1.0.1.
-- V1/V2 remain historical receipts for their exact predecessor subjects.
-- This receipt records source-registration state only; no compatibility, qualification,
-- installation, activation, assignment, authority, or currentness effect is implied.

DO $receipt$
DECLARE
  v_digest constant text := 'eec64f2fccd75b8a1212e2076f5ddf60821be8090dc9865e4511989fc267ae83';
  v_existing record;
BEGIN
  IF (SELECT count(*) FROM bt2.training_packages) <> 9 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V3_EXPECTED_9_PACKAGES';
  END IF;

  IF (SELECT count(*) FROM bt2.training_packages WHERE agent_key='four' AND version='1.0.1' AND package_tree_git_sha1='0953afaeeec7543697f97711e5a2326d954e9fa3') <> 1 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V3_FOUR_SUBJECT_MISSING';
  END IF;

  IF EXISTS (
    SELECT 1 FROM bt2.training_packages
    WHERE status <> 'REGISTERED'
       OR source_binding_state <> 'BYTE_PRESERVED_VERIFIED'
       OR compatibility_state <> 'UNASSESSED'
  ) THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V3_STATE_MISMATCH';
  END IF;

  IF (SELECT count(*) FROM bt2.training_qualifications) <> 0 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V3_QUALIFICATION_EFFECT_PRESENT';
  END IF;

  IF (SELECT count(*) FROM bt2.training_installation_events) <> 0 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V3_INSTALLATION_EFFECT_PRESENT';
  END IF;

  SELECT migration_digest_sha256,result_state,evidence
  INTO v_existing
  FROM bt2.migration_receipts
  WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V3';

  IF FOUND THEN
    IF v_existing.migration_digest_sha256 IS DISTINCT FROM v_digest
       OR v_existing.result_state <> 'VERIFIED'
       OR v_existing.evidence->>'registered_package_count' IS DISTINCT FROM '9'
       OR v_existing.evidence->>'four_step_blob' IS DISTINCT FROM 'c2ce2cd725032b81e8ef38756910949a0e8b008d' THEN
      RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V3_RECEIPT_CONFLICT';
    END IF;
    RETURN;
  END IF;

  INSERT INTO bt2.migration_receipts(
    migration_key,source_system,target_component,migration_digest_sha256,
    result_state,evidence,applied_at,verified_at
  ) VALUES(
    'BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V3',
    'GITHUB:thebrazenbeard/bt2',
    'WOWSQL:bt2.training_packages',
    v_digest,
    'VERIFIED',
    jsonb_build_object(
      'base_loader_blob','e313af9b735a06caf21d6d132d5afc5be8eab4ab',
      'four_step_blob','c2ce2cd725032b81e8ef38756910949a0e8b008d',
      'registered_package_count',9,
      'four_package_tree','0953afaeeec7543697f97711e5a2326d954e9fa3',
      'expected_status','REGISTERED',
      'expected_source_binding_state','BYTE_PRESERVED_VERIFIED',
      'expected_compatibility_state','UNASSESSED',
      'qualification_count',0,
      'installation_event_count',0,
      'qualification_effect','NONE',
      'runtime_installation_effect','NONE',
      'authority_effect','NONE',
      'predecessor_receipt','BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V2',
      'v2_receipt_disposition','HISTORICAL_VALID_FOR_8_PACKAGE_SUBJECT'
    ),
    clock_timestamp(),clock_timestamp()
  );
END
$receipt$;
