-- Four v1.0.1 incremental training-source frontier smoke.
-- Reconstructs the eight-package predecessor, then applies Four + V3 receipt.
-- Entire test rolls back. No qualification or installation evidence is created.

BEGIN;

INSERT INTO bt2.agent_units(unit_key,display_name,unit_type,orchestrator_agent_key)
VALUES
  ('build_team_four_test','BT2 Four frontier test','ORCHESTRATED_TEAM','one'),
  ('masamune_four_test','Masa + Mune Four frontier test','PAIRED_TEAM',NULL),
  ('hephaestus_four_test','Hephaestus Four frontier test','INDEPENDENT_AGENT',NULL);

INSERT INTO bt2.agents(agent_key,display_name,numerical_identity,unit_key,role_kind,role_summary)
VALUES
  ('one','One',1,'build_team_four_test','PRIMARY','CI primary'),
  ('two','Two',2,'build_team_four_test','SUBAGENT','CI subagent'),
  ('three','Three',3,'build_team_four_test','SUBAGENT','CI subagent'),
  ('four','Four',4,'build_team_four_test','SUBAGENT','CI subagent'),
  ('seven','Seven',7,'build_team_four_test','SUBAGENT','CI subagent'),
  ('eight','Eight',8,'build_team_four_test','SUBAGENT','CI subagent'),
  ('masa','Masa',NULL,'masamune_four_test','PAIRED','CI paired'),
  ('mune','Mune',NULL,'masamune_four_test','PAIRED','CI paired'),
  ('hephaestus','Hephaestus',NULL,'hephaestus_four_test','INDEPENDENT','CI independent');

INSERT INTO bt2.agent_relationships(source_agent_key,target_agent_key,relation_type)
VALUES
  ('one','two','ORCHESTRATES'),
  ('one','three','ORCHESTRATES'),
  ('one','four','ORCHESTRATES'),
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

-- Reconstruct predecessor frontier exactly.
\ir ../data/0001_verified_training_source_registry_v1.sql
\ir ../data/0002_verified_training_source_registry_receipt_v2.sql

DO $test$
BEGIN
  IF (SELECT count(*) FROM bt2.training_packages)<>8 THEN
    RAISE EXCEPTION 'FOUR_FRONTIER_PREDECESSOR_NOT_8';
  END IF;
  IF (SELECT count(*) FROM bt2.training_packages WHERE agent_key='four')<>0 THEN
    RAISE EXCEPTION 'FOUR_PRESENT_BEFORE_FRONTIER_STEP';
  END IF;
  IF (SELECT evidence->>'registered_package_count' FROM bt2.migration_receipts WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V2') IS DISTINCT FROM '8' THEN
    RAISE EXCEPTION 'V2_RECEIPT_NOT_BOUND_TO_8';
  END IF;
END
$test$;

-- Advance to Four/nine-package frontier.
\ir ../data/0003_four_verified_training_source_registration_v1.sql
\ir ../data/0004_verified_training_source_registry_receipt_v3.sql

DO $test$
DECLARE
  v_expected text[]:=ARRAY['eight:1.0.0','four:1.0.1','hephaestus:1.0.0','masa:1.0.0','mune:1.0.1','one:1.0.0','seven:1.0.0','three:1.0.0','two:1.0.0'];
  v_observed text[];
BEGIN
  SELECT array_agg(agent_key||':'||version ORDER BY agent_key,version)
  INTO v_observed FROM bt2.training_packages;
  IF v_observed IS DISTINCT FROM v_expected THEN
    RAISE EXCEPTION 'FOUR_FRONTIER_SUBJECT_SET_MISMATCH';
  END IF;

  IF (SELECT count(*) FROM bt2.training_packages)<>9 THEN
    RAISE EXCEPTION 'FOUR_FRONTIER_NOT_9';
  END IF;
  IF (SELECT count(*) FROM bt2.training_packages WHERE agent_key='four' AND version='1.0.1' AND package_tree_git_sha1='0953afaeeec7543697f97711e5a2326d954e9fa3')<>1 THEN
    RAISE EXCEPTION 'FOUR_FRONTIER_EXACT_SUBJECT_MISSING';
  END IF;
  IF EXISTS (SELECT 1 FROM bt2.training_packages WHERE status<>'REGISTERED' OR source_binding_state<>'BYTE_PRESERVED_VERIFIED' OR compatibility_state<>'UNASSESSED') THEN
    RAISE EXCEPTION 'FOUR_FRONTIER_STATE_COLLAPSED';
  END IF;
  IF (SELECT count(*) FROM bt2.training_qualifications)<>0 THEN
    RAISE EXCEPTION 'FOUR_FRONTIER_CREATED_QUALIFICATION';
  END IF;
  IF (SELECT count(*) FROM bt2.training_installation_events)<>0 THEN
    RAISE EXCEPTION 'FOUR_FRONTIER_CREATED_INSTALLATION';
  END IF;
  IF (SELECT evidence->>'registered_package_count' FROM bt2.migration_receipts WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V3') IS DISTINCT FROM '9' THEN
    RAISE EXCEPTION 'V3_RECEIPT_NOT_BOUND_TO_9';
  END IF;
END
$test$;

-- Replay only the incremental frontier steps. They must converge without rewriting V2.
\ir ../data/0003_four_verified_training_source_registration_v1.sql
\ir ../data/0004_verified_training_source_registry_receipt_v3.sql

DO $test$
BEGIN
  IF (SELECT count(*) FROM bt2.training_packages)<>9 THEN
    RAISE EXCEPTION 'FOUR_FRONTIER_REPLAY_NOT_IDEMPOTENT';
  END IF;
  IF (SELECT count(*) FROM bt2.training_packages WHERE agent_key='four' AND version='1.0.1')<>1 THEN
    RAISE EXCEPTION 'FOUR_FRONTIER_REPLAY_DUPLICATED';
  END IF;
  IF (SELECT count(*) FROM bt2.migration_receipts WHERE migration_key='BT2-TRAINING-FOUR-V1.0.1-BYTE-PRESERVATION-V1')<>1 THEN
    RAISE EXCEPTION 'FOUR_PRESERVATION_RECEIPT_REPLAY_DUPLICATED';
  END IF;
  IF (SELECT count(*) FROM bt2.migration_receipts WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V3')<>1 THEN
    RAISE EXCEPTION 'V3_RECEIPT_REPLAY_DUPLICATED';
  END IF;
  IF (SELECT evidence->>'registered_package_count' FROM bt2.migration_receipts WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V2') IS DISTINCT FROM '8' THEN
    RAISE EXCEPTION 'V2_RECEIPT_MUTATED_BY_V3_REPLAY';
  END IF;
END
$test$;

ROLLBACK;
