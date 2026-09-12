-- Project Lantern cohosted historical archive receipt V2.
-- Apply only after lantern_cohosted_history_v2.py succeeds.
-- V2 supersedes the failed V1 evidence subject; archived source row bytes are unchanged.
-- This receipt proves historical preservation only; it creates no active authority/currentness.

DO $receipt$
DECLARE
  v_digest constant text := 'cb3a397d14df77eb29374332dd4fdb1ad0a35b2cc25b626d66d0f30b1f8e6a21';
  v_source_system constant text := 'SUPABASE:agvhmutlrolbaijzlbqk:COHOSTED_HISTORY_V2';
  v_archive_sha constant text := '6ae6aad2fe494576a48ac505195c9315e932776c51a6f1c9480884bfa8185712';
  v_snapshot_id uuid;
  v_existing record;
BEGIN
  SELECT source_snapshot_id INTO STRICT v_snapshot_id
  FROM bt2.source_snapshots
  WHERE source_kind='SUPABASE'
    AND source_name='Project Lantern'
    AND canonical_locator='agvhmutlrolbaijzlbqk'
    AND source_ref='cohosted-historical-20260911-v2'
    AND source_commit=v_archive_sha
    AND metadata->>'classification'='HISTORICAL_PROVENANCE_ONLY'
    AND metadata->>'row_count'='16'
    AND metadata->'relation_rowset_sha256'->>'governance.project_notices'='09dd782f2218d5294d1fdb386cbdfb24b100a59eb03e62598c7c20a2c5129a78';

  IF (SELECT count(*) FROM bt2_legacy.source_rows WHERE source_system=v_source_system) <> 16 THEN
    RAISE EXCEPTION 'LANTERN_COHOSTED_V2_EXPECTED_16_ROWS';
  END IF;

  IF (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(row_data ORDER BY source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex') FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='bug_ops' AND source_relation='role_registry') <> 'f4c0ef4588f6c19d7a6291a6471de92b63b8f5fb4123a993d80ab67966da0055'
     OR (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(row_data ORDER BY source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex') FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='bug_ops' AND source_relation='system_config') <> '3987cace3a570249a24305c3feaf75e5309bf4f8c751e0a4c8fb116b3faf7203'
     OR (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(row_data ORDER BY source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex') FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='governance' AND source_relation='project_notices') <> '09dd782f2218d5294d1fdb386cbdfb24b100a59eb03e62598c7c20a2c5129a78'
     OR (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(row_data ORDER BY source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex') FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='r9a0_coordination' AND source_relation='events') <> '5ea2b175f869cd38b58121fe0273305c2bf1595c534fad44108f0ae1fb4746c4'
     OR (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(row_data ORDER BY source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex') FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='r9a0_governance' AND source_relation='migration_applications') <> 'b9e8cd36365aebfe4ae0a20d9c67e84c64e8fc63672e4a7fc71f97f59f963e8a' THEN
    RAISE EXCEPTION 'LANTERN_COHOSTED_V2_RELATION_DIGEST_MISMATCH';
  END IF;

  IF (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(jsonb_build_object(
      'source_schema',source_schema,
      'source_relation',source_relation,
      'source_primary_key',source_primary_key,
      'row_data',row_data
    ) ORDER BY source_schema,source_relation,source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex')
      FROM bt2_legacy.source_rows WHERE source_system=v_source_system) <> v_archive_sha THEN
    RAISE EXCEPTION 'LANTERN_COHOSTED_V2_COMBINED_DIGEST_MISMATCH';
  END IF;

  SELECT migration_digest_sha256,result_state,evidence INTO v_existing
  FROM bt2.migration_receipts
  WHERE migration_key='BT2-PROJECT-LANTERN-COHOSTED-HISTORY-V2';

  IF FOUND THEN
    IF v_existing.migration_digest_sha256 IS DISTINCT FROM v_digest
       OR v_existing.result_state <> 'VERIFIED'
       OR v_existing.evidence->>'archive_sha256' IS DISTINCT FROM v_archive_sha
       OR v_existing.evidence->>'row_count' IS DISTINCT FROM '16' THEN
      RAISE EXCEPTION 'LANTERN_COHOSTED_V2_RECEIPT_REPLAY_CONFLICT';
    END IF;
    RETURN;
  END IF;

  INSERT INTO bt2.migration_receipts(
    migration_key,source_system,target_component,migration_digest_sha256,
    result_state,evidence,source_snapshot_id,applied_at,verified_at
  ) VALUES(
    'BT2-PROJECT-LANTERN-COHOSTED-HISTORY-V2',
    'SUPABASE:agvhmutlrolbaijzlbqk',
    'bt2_legacy.source_rows',
    v_digest,
    'VERIFIED',
    jsonb_build_object(
      'classification','HISTORICAL_PROVENANCE_ONLY',
      'archive_sha256',v_archive_sha,
      'manifest_blob','d20ac718e6ac37cd15173fd4235cb5e78507ed80',
      'migration_blob','b73701ae43cc5141ba9d5be8145be3dfa84839a7',
      'loader_blob','39b5d129dc6679bf6a971c8f2af89a084013001c',
      'row_count',16,
      'governance_rowset_sha256','09dd782f2218d5294d1fdb386cbdfb24b100a59eb03e62598c7c20a2c5129a78',
      'supersedes_failed_subject','COHOSTED_HISTORY_V1',
      'replay_inserted',0,
      'authority_effect','NONE',
      'currentness_effect','NONE',
      'active_table_effect','NONE_BY_ONE_PREPOST_READBACK'
    ),
    v_snapshot_id,clock_timestamp(),clock_timestamp()
  );
END
$receipt$;
