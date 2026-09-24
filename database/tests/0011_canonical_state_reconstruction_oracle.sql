-- BT2 canonical-state reconstruction oracle V1.
-- Run after the persistent reconstruction sequence. Read-only: no fixture state.
-- Generated UUIDs for package/receipt internals are not compared where semantic keys
-- and immutable evidence digests define the durable subject.

SET TIME ZONE 'UTC';

DO $oracle$
DECLARE
  v_topology_digest text;
  v_lantern_digest text;
  v_expected_training text[] := ARRAY[
    'eight:1.0.0:5217e383cefad53b9ef97f6e35544b0e10f8da58',
    'five:1.0.0:f6c962e81c75deab3aa55d300fc4f9f9fa89f034',
    'four:1.0.1:0953afaeeec7543697f97711e5a2326d954e9fa3',
    'hephaestus:1.0.0:e14ea9f72bbe6e15151f78f3bd617526b22b57fa',
    'masa:1.0.0:96f8aa5f37dc8bb72d5ec270bf372e28a5b992a5',
    'mune:1.0.1:5e8c87021bfda9a6fc44fa121c32410ddc6aedf9',
    'nine:1.0.0:0738e13d0ce53a5f1368aa7472e2375fb491a3d9',
    'one:1.0.0:e27ce67b67159fb445347ae9a8888fe3c480cdd1',
    'seven:1.0.0:86b38a66d7bb5d6b71e1bf9754dee3248e2e9792',
    'six:1.0.0:ba3ffa8adc18f635e516356a92e7d0450fa7a789',
    'thirteen:1.0.0:3cc36d9aef3f84cbc2d9d808ff3d92d3714faf5e',
    'three:1.0.0:696484549f1e729bb04b546e50973efc1fa4439c',
    'two:1.0.0:e42eeb5c3c269b8e42aa955b1e85846d63eafe98'
  ];
  v_observed_training text[];
  v_secdef boolean;
  v_owner text;
  v_config text[];
  v_public_exec boolean;
  v_postgres_exec boolean;
BEGIN
  -- Exact current workforce topology.
  WITH topo AS (
    SELECT jsonb_build_object(
      'units',(SELECT jsonb_agg(jsonb_build_array(unit_key,display_name,unit_type,orchestrator_agent_key,active,description) ORDER BY unit_key) FROM bt2.agent_units),
      'agents',(SELECT jsonb_agg(jsonb_build_array(agent_key,display_name,numerical_identity,unit_key,role_kind,role_summary,active,training_required) ORDER BY agent_key) FROM bt2.agents),
      'relationships',(SELECT jsonb_agg(jsonb_build_array(source_agent_key,target_agent_key,relation_type,active) ORDER BY source_agent_key,target_agent_key,relation_type) FROM bt2.agent_relationships)
    ) AS doc
  )
  SELECT encode(public.digest(convert_to(doc::text,'UTF8'),'sha256'),'hex') INTO v_topology_digest FROM topo;

  IF v_topology_digest <> '45d262aae7285a69a66a3d5b35c04537899ba33f5eb7388b9731071e8907c0d8' THEN
    RAISE EXCEPTION 'BT2_REBUILD_TOPOLOGY_DIGEST_MISMATCH:%',v_topology_digest;
  END IF;

  -- Exact current preserved package subject set; preservation must not imply qualification/install.
  SELECT array_agg(agent_key||':'||version||':'||package_tree_git_sha1 ORDER BY agent_key,version)
  INTO v_observed_training
  FROM bt2.training_packages;

  IF v_observed_training IS DISTINCT FROM v_expected_training THEN
    RAISE EXCEPTION 'BT2_REBUILD_TRAINING_FRONTIER_MISMATCH:%',v_observed_training;
  END IF;

  IF EXISTS (
    SELECT 1 FROM bt2.training_packages
    WHERE status <> 'REGISTERED'
       OR source_binding_state <> 'BYTE_PRESERVED_VERIFIED'
       OR compatibility_state <> 'UNASSESSED'
  ) THEN
    RAISE EXCEPTION 'BT2_REBUILD_TRAINING_STATE_COLLAPSED';
  END IF;

  IF (SELECT count(*) FROM bt2.training_qualifications) <> 0
     OR (SELECT count(*) FROM bt2.training_installation_events) <> 0 THEN
    RAISE EXCEPTION 'BT2_REBUILD_FABRICATED_TRAINING_QUALIFICATION_OR_INSTALLATION';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM bt2.migration_receipts
    WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V4'
      AND result_state='VERIFIED'
      AND evidence->>'registered_package_count'='13'
      AND evidence->>'frontier_digest_sha256'='8c30820432c95f5fd0e663cd6054c522b41b18c0979ce11c06e967037116eabc'
  ) THEN
    RAISE EXCEPTION 'BT2_REBUILD_TRAINING_V4_RECEIPT_MISSING';
  END IF;

  -- Exact governed Lantern current state.
  WITH state AS (
    SELECT jsonb_build_object(
      'policy',(SELECT jsonb_agg(to_jsonb(p) ORDER BY schema_version) FROM bt2.material_schema_policy p WHERE schema_version='LANTERN_MATERIAL_V1'),
      'profile',(SELECT jsonb_agg(to_jsonb(p) ORDER BY project_scope,profile_digest) FROM bt2.material_profiles p WHERE project_scope='PROJECT_LANTERN'),
      'permits',(SELECT jsonb_agg(to_jsonb(p) ORDER BY permit_id) FROM bt2.material_producer_permits p WHERE project_scope='PROJECT_LANTERN'),
      'materials',(SELECT jsonb_agg(to_jsonb(m) ORDER BY material_id) FROM bt2.materials m WHERE project_scope='PROJECT_LANTERN'),
      'receipts',(SELECT jsonb_agg(to_jsonb(r) ORDER BY receipt_id) FROM bt2.material_receipts r WHERE project_scope='PROJECT_LANTERN')
    ) AS doc
  )
  SELECT encode(public.digest(convert_to(doc::text,'UTF8'),'sha256'),'hex') INTO v_lantern_digest FROM state;

  IF v_lantern_digest <> '29da0892c199207bf566e8cf62c0ae8921d63950796fd58204577c464ca59dc5' THEN
    RAISE EXCEPTION 'BT2_REBUILD_LANTERN_STATE_DIGEST_MISMATCH:%',v_lantern_digest;
  END IF;

  IF EXISTS (
    SELECT 1 FROM bt2.material_producer_permits
    WHERE project_scope='PROJECT_LANTERN'
      AND invalidated_at IS NULL
      AND valid_from <= clock_timestamp()
      AND valid_until > clock_timestamp()
  ) THEN
    RAISE EXCEPTION 'BT2_REBUILD_CREATED_CURRENT_LANTERN_PRODUCER_AUTHORITY';
  END IF;

  -- Cohosted source history remains historical-only and exact.
  IF (SELECT count(*) FROM bt2_legacy.source_rows
      WHERE source_system='SUPABASE:agvhmutlrolbaijzlbqk:COHOSTED_HISTORY_V2') <> 16 THEN
    RAISE EXCEPTION 'BT2_REBUILD_LANTERN_HISTORY_ROW_COUNT_MISMATCH';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM bt2.migration_receipts
    WHERE migration_key='BT2-PROJECT-LANTERN-COHOSTED-HISTORY-V2'
      AND result_state='VERIFIED'
      AND evidence->>'archive_sha256'='6ae6aad2fe494576a48ac505195c9315e932776c51a6f1c9480884bfa8185712'
  ) THEN
    RAISE EXCEPTION 'BT2_REBUILD_LANTERN_HISTORY_V2_RECEIPT_MISSING';
  END IF;

  -- Evidence ledger itself must still be immutable.
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger tg
    JOIN pg_class c ON c.oid=tg.tgrelid
    JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='bt2' AND c.relname='migration_receipts'
      AND tg.tgname='migration_receipts_no_update_delete_v1' AND NOT tg.tgisinternal
  ) THEN
    RAISE EXCEPTION 'BT2_REBUILD_MIGRATION_RECEIPT_LEDGER_NOT_APPEND_ONLY';
  END IF;

  -- The source-designed producer boundary must be installed in a real PG16 rebuild.
  SELECT p.prosecdef,p.proowner::regrole::text,p.proconfig,
         has_function_privilege('public','bt2.append_material_v1(uuid,text,text,text,text,text)','EXECUTE'),
         has_function_privilege('postgres','bt2.append_material_v1(uuid,text,text,text,text,text)','EXECUTE')
  INTO v_secdef,v_owner,v_config,v_public_exec,v_postgres_exec
  FROM pg_proc p
  JOIN pg_namespace n ON n.oid=p.pronamespace
  WHERE n.nspname='bt2' AND p.proname='append_material_v1'
    AND oidvectortypes(p.proargtypes)='uuid, text, text, text, text, text';

  IF NOT coalesce(v_secdef,false)
     OR v_owner <> 'postgres'
     OR NOT coalesce(v_config @> ARRAY['search_path=pg_catalog, bt2, pg_temp']::text[],false)
     OR coalesce(v_public_exec,true)
     OR NOT coalesce(v_postgres_exec,false) THEN
    RAISE EXCEPTION 'BT2_REBUILD_LANTERN_PRODUCER_BOUNDARY_MISMATCH';
  END IF;
END
$oracle$;

SELECT 'BT2_CANONICAL_STATE_RECONSTRUCTION_PASS' AS result;
