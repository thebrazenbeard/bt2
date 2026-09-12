-- BT2 training-source registry population receipt V2.
-- This preserves V1 as historical evidence for the earlier seven-package subject.
-- V2 binds the current eight-package source-load subject without changing package,
-- compatibility, qualification, installation, assignment, authority, or currentness state.

DO $receipt$
DECLARE
  v_digest constant text := 'ab185318e8865136228efd684382d3e67601abfa357ffcabc3be6ca1c8312e11';
  v_existing record;
BEGIN
  IF (SELECT count(*) FROM bt2.training_packages) <> 8 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V2_EXPECTED_8_PACKAGES';
  END IF;

  IF EXISTS (
    SELECT 1 FROM bt2.training_packages
    WHERE status <> 'REGISTERED'
       OR source_binding_state <> 'BYTE_PRESERVED_VERIFIED'
       OR compatibility_state <> 'UNASSESSED'
  ) THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V2_STATE_MISMATCH';
  END IF;

  IF (SELECT count(*) FROM bt2.training_qualifications) <> 0 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V2_QUALIFICATION_EFFECT_PRESENT';
  END IF;

  IF (SELECT count(*) FROM bt2.training_installation_events) <> 0 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V2_INSTALLATION_EFFECT_PRESENT';
  END IF;

  SELECT mr.migration_digest_sha256,mr.result_state,mr.evidence
  INTO v_existing
  FROM bt2.migration_receipts mr
  WHERE mr.migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V2';

  IF FOUND THEN
    IF v_existing.migration_digest_sha256 IS DISTINCT FROM v_digest
       OR v_existing.result_state <> 'VERIFIED'
       OR v_existing.evidence->>'data_script_blob' IS DISTINCT FROM 'e313af9b735a06caf21d6d132d5afc5be8eab4ab'
       OR v_existing.evidence->>'reconstruction_test_blob' IS DISTINCT FROM '31c96a79b5382c6825254a047a3259be7a3b70a6'
       OR v_existing.evidence->>'registered_package_count' IS DISTINCT FROM '8' THEN
      RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V2_RECEIPT_CONFLICT';
    END IF;
    RETURN;
  END IF;

  INSERT INTO bt2.migration_receipts(
    migration_key,source_system,target_component,migration_digest_sha256,
    result_state,evidence,applied_at,verified_at
  ) VALUES(
    'BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V2',
    'GITHUB:thebrazenbeard/bt2',
    'WOWSQL:bt2.training_packages',
    v_digest,
    'VERIFIED',
    jsonb_build_object(
      'data_script_blob','e313af9b735a06caf21d6d132d5afc5be8eab4ab',
      'reconstruction_test_blob','31c96a79b5382c6825254a047a3259be7a3b70a6',
      'registered_package_count',8,
      'expected_status','REGISTERED',
      'expected_source_binding_state','BYTE_PRESERVED_VERIFIED',
      'expected_compatibility_state','UNASSESSED',
      'qualification_count',0,
      'installation_event_count',0,
      'qualification_effect','NONE',
      'runtime_installation_effect','NONE',
      'authority_effect','NONE',
      'supersedes_receipt_subject','BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V1_AS_CURRENT_REGISTRY_PROOF',
      'v1_receipt_disposition','HISTORICAL_VALID_FOR_7_PACKAGE_SUBJECT'
    ),
    clock_timestamp(),clock_timestamp()
  );
END
$receipt$;
