-- Project Lantern cohosted historical archive receipt V1.
-- Apply only after lantern_cohosted_history_v1.py --mode apply succeeds.
-- This receipt proves historical preservation only; it creates no active authority/currentness.

DO $receipt$
DECLARE
  v_digest constant text := 'bd5ae9b75bb0efae51864eecb74508008304fee668a7272090fdc205bdb7efdc';
  v_source_system constant text := 'SUPABASE:agvhmutlrolbaijzlbqk:COHOSTED_HISTORY_V1';
  v_archive_sha constant text := '6ae6aad2fe494576a48ac505195c9315e932776c51a6f1c9480884bfa8185712';
  v_snapshot_id uuid;
  v_existing record;
BEGIN
  SELECT source_snapshot_id INTO STRICT v_snapshot_id
  FROM bt2.source_snapshots
  WHERE source_kind='SUPABASE'
    AND source_name='Project Lantern'
    AND canonical_locator='agvhmutlrolbaijzlbqk'
    AND source_ref='cohosted-historical-20260911-v1'
    AND source_commit=v_archive_sha
    AND metadata->>'classification'='HISTORICAL_PROVENANCE_ONLY'
    AND metadata->>'row_count'='16';

  IF (SELECT count(*) FROM bt2_legacy.source_rows WHERE source_system=v_source_system) <> 16 THEN
    RAISE EXCEPTION 'LANTERN_COHOSTED_RECEIPT_EXPECTED_16_ROWS';
  END IF;

  IF (SELECT count(*) FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='bug_ops' AND source_relation='role_registry') <> 4
     OR (SELECT count(*) FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='bug_ops' AND source_relation='system_config') <> 1
     OR (SELECT count(*) FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='governance' AND source_relation='project_notices') <> 7
     OR (SELECT count(*) FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='r9a0_coordination' AND source_relation='events') <> 3
     OR (SELECT count(*) FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='r9a0_governance' AND source_relation='migration_applications') <> 1 THEN
    RAISE EXCEPTION 'LANTERN_COHOSTED_RECEIPT_RELATION_COUNTS_MISMATCH';
  END IF;

  IF (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(row_data ORDER BY source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex') FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='bug_ops' AND source_relation='role_registry') <> 'f4c0ef4588f6c19d7a6291a6471de92b63b8f5fb4123a993d80ab67966da0055'
     OR (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(row_data ORDER BY source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex') FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='bug_ops' AND source_relation='system_config') <> '3987cace3a570249a24305c3feaf75e5309bf4f8c751e0a4c8fb116b3faf7203'
     OR (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(row_data ORDER BY source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex') FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='governance' AND source_relation='project_notices') <> 'a57ad620a1849fafe2426e0867d2119f75c553bd9829793665bafe79e7bdc0e0'
     OR (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(row_data ORDER BY source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex') FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='r9a0_coordination' AND source_relation='events') <> '5ea2b175f869cd38b58121fe0273305c2bf1595c534fad44108f0ae1fb4746c4'
     OR (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(row_data ORDER BY source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex') FROM bt2_legacy.source_rows WHERE source_system=v_source_system AND source_schema='r9a0_governance' AND source_relation='migration_applications') <> 'b9e8cd36365aebfe4ae0a20d9c67e84c64e8fc63672e4a7fc71f97f59f963e8a' THEN
    RAISE EXCEPTION 'LANTERN_COHOSTED_RECEIPT_RELATION_DIGEST_MISMATCH';
  END IF;

  IF (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(jsonb_build_object(
      'source_schema',source_schema,
      'source_relation',source_relation,
      'source_primary_key',source_primary_key,
      'row_data',row_data
    ) ORDER BY source_schema,source_relation,source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex')
      FROM bt2_legacy.source_rows WHERE source_system=v_source_system) <> v_archive_sha THEN
    RAISE EXCEPTION 'LANTERN_COHOSTED_RECEIPT_COMBINED_DIGEST_MISMATCH';
  END IF;

  SELECT migration_digest_sha256,result_state,evidence INTO v_existing
  FROM bt2.migration_receipts
  WHERE migration_key='BT2-PROJECT-LANTERN-COHOSTED-HISTORY-V1';

  IF FOUND THEN
    IF v_existing.migration_digest_sha256 IS DISTINCT FROM v_digest
       OR v_existing.result_state <> 'VERIFIED'
       OR v_existing.evidence->>'archive_sha256' IS DISTINCT FROM v_archive_sha
       OR v_existing.evidence->>'row_count' IS DISTINCT FROM '16' THEN
      RAISE EXCEPTION 'LANTERN_COHOSTED_RECEIPT_REPLAY_CONFLICT';
    END IF;
    RETURN;
  END IF;

  INSERT INTO bt2.migration_receipts(
    migration_key,source_system,target_component,migration_digest_sha256,
    result_state,evidence,source_snapshot_id,applied_at,verified_at
  ) VALUES(
    'BT2-PROJECT-LANTERN-COHOSTED-HISTORY-V1',
    'SUPABASE:agvhmutlrolbaijzlbqk',
    'bt2_legacy.source_rows',
    v_digest,
    'VERIFIED',
    jsonb_build_object(
      'classification','HISTORICAL_PROVENANCE_ONLY',
      'archive_sha256',v_archive_sha,
      'archive_tree','0aae7f220704d34e101d43ae1102a1b51dd5776a',
      'migration_blob','3a05a86e0a7b921bfd264c30bccd57cb4fdef093',
      'loader_blob','a57d05b5bfff1a2dbd8268e69acc32097b68cd7b',
      'row_count',16,
      'relation_counts',jsonb_build_object(
        'bug_ops.role_registry',4,
        'bug_ops.system_config',1,
        'governance.project_notices',7,
        'r9a0_coordination.events',3,
        'r9a0_governance.migration_applications',1
      ),
      'authority_effect','NONE',
      'currentness_effect','NONE',
      'active_table_effect','NONE_BY_LOADER_PREPOST_ORACLE'
    ),
    v_snapshot_id,clock_timestamp(),clock_timestamp()
  );
END
$receipt$;
