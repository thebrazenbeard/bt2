-- BT2 preserved training-source registry reconstruction smoke.
-- Synthetic preservation receipts only; invokes the real post-preservation data load twice.
-- Entire test rolls back. No qualification or installation evidence is created.

BEGIN;

INSERT INTO bt2.agent_units(unit_key,display_name,unit_type,orchestrator_agent_key)
VALUES
  ('build_team_registry_test','BT2 registry test','ORCHESTRATED_TEAM','one'),
  ('masamune_registry_test','Masa + Mune registry test','PAIRED_TEAM',NULL),
  ('hephaestus_registry_test','Hephaestus registry test','INDEPENDENT_AGENT',NULL);

INSERT INTO bt2.agents(agent_key,display_name,numerical_identity,unit_key,role_kind,role_summary)
VALUES
  ('one','One',1,'build_team_registry_test','PRIMARY','CI primary'),
  ('two','Two',2,'build_team_registry_test','SUBAGENT','CI subagent'),
  ('three','Three',3,'build_team_registry_test','SUBAGENT','CI subagent'),
  ('seven','Seven',7,'build_team_registry_test','SUBAGENT','CI subagent'),
  ('eight','Eight',8,'build_team_registry_test','SUBAGENT','CI subagent'),
  ('masa','Masa',NULL,'masamune_registry_test','PAIRED','CI paired'),
  ('mune','Mune',NULL,'masamune_registry_test','PAIRED','CI paired'),
  ('hephaestus','Hephaestus',NULL,'hephaestus_registry_test','INDEPENDENT','CI independent');

INSERT INTO bt2.agent_relationships(source_agent_key,target_agent_key,relation_type)
VALUES
  ('one','two','ORCHESTRATES'),
  ('one','three','ORCHESTRATES'),
  ('one','seven','ORCHESTRATES'),
  ('one','eight','ORCHESTRATES'),
  ('masa','mune','PAIRED_WITH'),
  ('mune','masa','PAIRED_WITH');

INSERT INTO bt2.migration_receipts(
  migration_key,source_system,target_component,migration_digest_sha256,result_state,evidence,applied_at,verified_at
)
SELECT v.migration_key,'CI_PRESERVATION','training-source-registry',
       encode(public.digest(convert_to(v.migration_key,'UTF8'),'sha256'),'hex'),
       'VERIFIED',
       jsonb_build_object(
         'source_package_tree',v.package_tree,
         'target_package_tree',v.package_tree,
         'qualification_effect','NONE',
         'runtime_installation_effect','NONE',
         'authority_effect','NONE'
       ),clock_timestamp(),clock_timestamp()
FROM (VALUES
  ('BT2-TRAINING-ONE-V1.0.0-BYTE-PRESERVATION-V1','e27ce67b67159fb445347ae9a8888fe3c480cdd1'),
  ('BT2-TRAINING-TWO-V1.0.0-BYTE-PRESERVATION-V1','e42eeb5c3c269b8e42aa955b1e85846d63eafe98'),
  ('BT2-TRAINING-THREE-V1.0.0-BYTE-PRESERVATION-V1','696484549f1e729bb04b546e50973efc1fa4439c'),
  ('BT2-TRAINING-SEVEN-V1.0.0-BYTE-PRESERVATION-V1','86b38a66d7bb5d6b71e1bf9754dee3248e2e9792'),
  ('BT2-TRAINING-EIGHT-V1.0.0-BYTE-PRESERVATION-V1','5217e383cefad53b9ef97f6e35544b0e10f8da58'),
  ('BT2-TRAINING-MASA-V1.0.0-BYTE-PRESERVATION-V1','96f8aa5f37dc8bb72d5ec270bf372e28a5b992a5'),
  ('BT2-TRAINING-MUNE-V1.0.1-BYTE-PRESERVATION-V1','5e8c87021bfda9a6fc44fa121c32410ddc6aedf9'),
  ('BT2-TRAINING-HEPHAESTUS-V1.0.0-BYTE-PRESERVATION-V1','e14ea9f72bbe6e15151f78f3bd617526b22b57fa')
) AS v(migration_key,package_tree);

-- First reconstruction.
\ir ../data/0001_verified_training_source_registry_v1.sql

DO $test$
DECLARE v_expected text[]:=ARRAY['eight:1.0.0','hephaestus:1.0.0','masa:1.0.0','mune:1.0.1','one:1.0.0','seven:1.0.0','three:1.0.0','two:1.0.0'];
DECLARE v_observed text[];
BEGIN
  SELECT array_agg(agent_key||':'||version ORDER BY agent_key,version)
  INTO v_observed
  FROM bt2.training_packages;

  IF v_observed IS DISTINCT FROM v_expected THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_SUBJECT_SET_MISMATCH';
  END IF;

  IF EXISTS (
    SELECT 1 FROM bt2.training_packages
    WHERE status<>'REGISTERED'
       OR source_binding_state<>'BYTE_PRESERVED_VERIFIED'
       OR compatibility_state<>'UNASSESSED'
  ) THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_STATE_COLLAPSED';
  END IF;

  IF (SELECT count(*) FROM bt2.training_qualifications)<>0 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_LOAD_CREATED_QUALIFICATION';
  END IF;
  IF (SELECT count(*) FROM bt2.training_installation_events)<>0 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_LOAD_CREATED_INSTALLATION_EVENT';
  END IF;
END
$test$;

-- Replay the exact source load. It must converge, not duplicate.
\ir ../data/0001_verified_training_source_registry_v1.sql

DO $test$
BEGIN
  IF (SELECT count(*) FROM bt2.training_packages)<>8 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REGISTRY_REPLAY_NOT_IDEMPOTENT';
  END IF;
  IF (SELECT count(*) FROM bt2.training_packages WHERE agent_key='one' AND version='1.0.0')<>1 THEN
    RAISE EXCEPTION 'ONE_REGISTRY_REPLAY_DUPLICATED_OR_MISSING';
  END IF;
  IF (SELECT count(*) FROM bt2.training_qualifications)<>0 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REPLAY_CREATED_QUALIFICATION';
  END IF;
  IF (SELECT count(*) FROM bt2.training_installation_events)<>0 THEN
    RAISE EXCEPTION 'TRAINING_SOURCE_REPLAY_CREATED_INSTALLATION_EVENT';
  END IF;
END
$test$;

ROLLBACK;
