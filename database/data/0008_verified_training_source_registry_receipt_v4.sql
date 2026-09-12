-- Registry frontier receipt V4: complete current preserved training-source set.
-- This receipt records source-registration state only; no compatibility, qualification,
-- installation, activation, assignment, authority, or currentness effect is implied.
-- Frontier digest rule: SHA256 of lexicographically sorted agent:version:package_tree tuples joined by '|'.

DO $receipt$
DECLARE
  v_digest constant text := 'add9d499abba0f0810448cf1cc22ec0f81ae2273fab81817c52f1d20a9e48710';
  v_frontier_digest constant text := '8c30820432c95f5fd0e663cd6054c522b41b18c0979ce11c06e967037116eabc';
  v_existing record;
BEGIN
  IF (SELECT count(*) FROM bt2.training_packages) <> 13 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V4_EXPECTED_13_PACKAGES';
  END IF;

  IF EXISTS (
    SELECT 1 FROM bt2.training_packages
    WHERE status <> 'REGISTERED'
       OR source_binding_state <> 'BYTE_PRESERVED_VERIFIED'
       OR compatibility_state <> 'UNASSESSED'
  ) THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V4_STATE_MISMATCH';
  END IF;

  IF (SELECT count(*) FROM bt2.training_qualifications) <> 0 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V4_QUALIFICATION_EFFECT_PRESENT';
  END IF;

  IF (SELECT count(*) FROM bt2.training_installation_events) <> 0 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V4_INSTALLATION_EFFECT_PRESENT';
  END IF;

  IF EXISTS (
    WITH expected(agent_key,version,package_tree) AS (
      VALUES
        ('one','1.0.0','e27ce67b67159fb445347ae9a8888fe3c480cdd1'),
        ('two','1.0.0','e42eeb5c3c269b8e42aa955b1e85846d63eafe98'),
        ('three','1.0.0','696484549f1e729bb04b546e50973efc1fa4439c'),
        ('four','1.0.1','0953afaeeec7543697f97711e5a2326d954e9fa3'),
        ('five','1.0.0','f6c962e81c75deab3aa55d300fc4f9f9fa89f034'),
        ('six','1.0.0','ba3ffa8adc18f635e516356a92e7d0450fa7a789'),
        ('seven','1.0.0','86b38a66d7bb5d6b71e1bf9754dee3248e2e9792'),
        ('eight','1.0.0','5217e383cefad53b9ef97f6e35544b0e10f8da58'),
        ('nine','1.0.0','0738e13d0ce53a5f1368aa7472e2375fb491a3d9'),
        ('thirteen','1.0.0','3cc36d9aef3f84cbc2d9d808ff3d92d3714faf5e'),
        ('masa','1.0.0','96f8aa5f37dc8bb72d5ec270bf372e28a5b992a5'),
        ('mune','1.0.1','5e8c87021bfda9a6fc44fa121c32410ddc6aedf9'),
        ('hephaestus','1.0.0','e14ea9f72bbe6e15151f78f3bd617526b22b57fa')
    )
    SELECT 1
    FROM expected e
    LEFT JOIN bt2.training_packages p
      ON p.agent_key=e.agent_key
     AND p.version=e.version
     AND p.package_tree_git_sha1=e.package_tree
    WHERE p.training_package_id IS NULL
  ) THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V4_EXACT_SUBJECT_MISSING';
  END IF;

  SELECT migration_digest_sha256,result_state,evidence
  INTO v_existing
  FROM bt2.migration_receipts
  WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V4';

  IF FOUND THEN
    IF v_existing.migration_digest_sha256 IS DISTINCT FROM v_digest
       OR v_existing.result_state <> 'VERIFIED'
       OR v_existing.evidence->>'registered_package_count' IS DISTINCT FROM '13'
       OR v_existing.evidence->>'frontier_digest_sha256' IS DISTINCT FROM v_frontier_digest THEN
      RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_V4_RECEIPT_CONFLICT';
    END IF;
    RETURN;
  END IF;

  INSERT INTO bt2.migration_receipts(
    migration_key,source_system,target_component,migration_digest_sha256,
    result_state,evidence,applied_at,verified_at
  ) VALUES(
    'BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V4',
    'GITHUB:thebrazenbeard/bt2',
    'WOWSQL:bt2.training_packages',
    v_digest,
    'VERIFIED',
    jsonb_build_object(
      'registered_package_count',13,
      'frontier_digest_sha256',v_frontier_digest,
      'remaining_numbered_registration_source','database/data/0007_remaining_numbered_training_source_registration_v1.sql',
      'five_package_tree','f6c962e81c75deab3aa55d300fc4f9f9fa89f034',
      'six_package_tree','ba3ffa8adc18f635e516356a92e7d0450fa7a789',
      'nine_package_tree','0738e13d0ce53a5f1368aa7472e2375fb491a3d9',
      'thirteen_package_tree','3cc36d9aef3f84cbc2d9d808ff3d92d3714faf5e',
      'expected_status','REGISTERED',
      'expected_source_binding_state','BYTE_PRESERVED_VERIFIED',
      'expected_compatibility_state','UNASSESSED',
      'qualification_count',0,
      'installation_event_count',0,
      'qualification_effect','NONE',
      'runtime_installation_effect','NONE',
      'authority_effect','NONE',
      'predecessor_receipt','BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V3',
      'v3_receipt_disposition','HISTORICAL_VALID_FOR_9_PACKAGE_SUBJECT'
    ),
    clock_timestamp(),clock_timestamp()
  );
END
$receipt$;
