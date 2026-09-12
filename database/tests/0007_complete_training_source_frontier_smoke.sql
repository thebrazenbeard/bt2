-- Complete 13-package training-source frontier smoke.
-- Reconstructs V2 (8 packages), V3 (9 packages), then applies the four remaining
-- numbered package registrations and V4 (13 packages). Entire test rolls back.
-- Preservation must never create compatibility, qualification, installation, activation,
-- assignment, authority, or currentness effects.

BEGIN;

INSERT INTO bt2.agent_units(unit_key,display_name,unit_type,orchestrator_agent_key)
VALUES
  ('build_team_complete_frontier_test','BT2 complete frontier test','ORCHESTRATED_TEAM','one'),
  ('masamune_complete_frontier_test','Masa + Mune complete frontier test','PAIRED_TEAM',NULL),
  ('hephaestus_complete_frontier_test','Hephaestus complete frontier test','INDEPENDENT_AGENT',NULL);

INSERT INTO bt2.agents(agent_key,display_name,numerical_identity,unit_key,role_kind,role_summary)
VALUES
  ('one','One',1,'build_team_complete_frontier_test','PRIMARY','CI primary'),
  ('two','Two',2,'build_team_complete_frontier_test','SUBAGENT','CI subagent'),
  ('three','Three',3,'build_team_complete_frontier_test','SUBAGENT','CI subagent'),
  ('four','Four',4,'build_team_complete_frontier_test','SUBAGENT','CI subagent'),
  ('five','Five',5,'build_team_complete_frontier_test','SUBAGENT','CI subagent'),
  ('six','Six',6,'build_team_complete_frontier_test','SUBAGENT','CI subagent'),
  ('seven','Seven',7,'build_team_complete_frontier_test','SUBAGENT','CI subagent'),
  ('eight','Eight',8,'build_team_complete_frontier_test','SUBAGENT','CI subagent'),
  ('nine','Nine',9,'build_team_complete_frontier_test','SUBAGENT','CI subagent'),
  ('thirteen','Thirteen',13,'build_team_complete_frontier_test','SUBAGENT','CI subagent'),
  ('masa','Masa',NULL,'masamune_complete_frontier_test','PAIRED','CI paired'),
  ('mune','Mune',NULL,'masamune_complete_frontier_test','PAIRED','CI paired'),
  ('hephaestus','Hephaestus',NULL,'hephaestus_complete_frontier_test','INDEPENDENT','CI independent');

INSERT INTO bt2.agent_relationships(source_agent_key,target_agent_key,relation_type)
VALUES
  ('one','two','ORCHESTRATES'),
  ('one','three','ORCHESTRATES'),
  ('one','four','ORCHESTRATES'),
  ('one','five','ORCHESTRATES'),
  ('one','six','ORCHESTRATES'),
  ('one','seven','ORCHESTRATES'),
  ('one','eight','ORCHESTRATES'),
  ('one','nine','ORCHESTRATES'),
  ('one','thirteen','ORCHESTRATES'),
  ('masa','mune','PAIRED_WITH'),
  ('mune','masa','PAIRED_WITH');

-- Seed only the eight predecessor preservation receipts. Four and the remaining
-- numbered roles must create their own exact package-level receipts through the
-- incremental source steps under test.
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

-- Reconstruct the exact predecessor chain first.
\ir ../data/0001_verified_training_source_registry_v1.sql
\ir ../data/0002_verified_training_source_registry_receipt_v2.sql
\ir ../data/0003_four_verified_training_source_registration_v1.sql
\ir ../data/0004_verified_training_source_registry_receipt_v3.sql

DO $test$
BEGIN
  IF (SELECT count(*) FROM bt2.training_packages)<>9 THEN
    RAISE EXCEPTION 'COMPLETE_FRONTIER_PREDECESSOR_NOT_9';
  END IF;
  IF (SELECT count(*) FROM bt2.training_packages WHERE agent_key IN ('five','six','nine','thirteen'))<>0 THEN
    RAISE EXCEPTION 'COMPLETE_FRONTIER_NEW_SUBJECT_PRESENT_BEFORE_STEP';
  END IF;
  IF (SELECT evidence->>'registered_package_count' FROM bt2.migration_receipts WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V3') IS DISTINCT FROM '9' THEN
    RAISE EXCEPTION 'V3_RECEIPT_NOT_BOUND_TO_9';
  END IF;
END
$test$;

-- Advance from the 9-package predecessor to the complete 13-package frontier.
\ir ../data/0007_remaining_numbered_training_source_registration_v1.sql
\ir ../data/0008_verified_training_source_registry_receipt_v4.sql

DO $test$
DECLARE
  v_expected text[]:=ARRAY[
    'eight:1.0.0','five:1.0.0','four:1.0.1','hephaestus:1.0.0','masa:1.0.0',
    'mune:1.0.1','nine:1.0.0','one:1.0.0','seven:1.0.0','six:1.0.0',
    'thirteen:1.0.0','three:1.0.0','two:1.0.0'
  ];
  v_observed text[];
BEGIN
  SELECT array_agg(agent_key||':'||version ORDER BY agent_key,version)
  INTO v_observed FROM bt2.training_packages;
  IF v_observed IS DISTINCT FROM v_expected THEN
    RAISE EXCEPTION 'COMPLETE_FRONTIER_SUBJECT_SET_MISMATCH';
  END IF;

  IF (SELECT count(*) FROM bt2.training_packages)<>13 THEN
    RAISE EXCEPTION 'COMPLETE_FRONTIER_NOT_13';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM bt2.training_packages
    WHERE agent_key='five' AND version='1.0.0'
      AND source_commit='da419ea83323c54908380c6ad57d65ea2c580f14'
      AND source_tree='912f329cf1f780171827a64b7bc8ce65512a1efa'
      AND source_package_path='training/roles/five/v1.0.0'
      AND package_tree_git_sha1='f6c962e81c75deab3aa55d300fc4f9f9fa89f034'
      AND manifest_blob_git_sha1='124db5b0aca892f05506d0a7086c8d9a2c9cd83f'
  ) THEN RAISE EXCEPTION 'FIVE_EXACT_SOURCE_BINDING_MISSING'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM bt2.training_packages
    WHERE agent_key='six' AND version='1.0.0'
      AND source_commit='fcb358b0e7ca7b1b57cf868e34aac28d5c0e55c4'
      AND source_tree='333adfc841c25e3e9a407f6c666ed2b7d51a402b'
      AND source_package_path='training/roles/six/v1.0.0'
      AND package_tree_git_sha1='ba3ffa8adc18f635e516356a92e7d0450fa7a789'
      AND manifest_blob_git_sha1='bc6906f8dd5c41712fea3691c167b14a39ffd7b9'
  ) THEN RAISE EXCEPTION 'SIX_EXACT_SOURCE_BINDING_MISSING'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM bt2.training_packages
    WHERE agent_key='nine' AND version='1.0.0'
      AND source_commit='a25c05f6c475dc96eb1c72900432ab4e74cb5acd'
      AND source_tree='faf7501b8f93aeca2346b3848131d7386f6c86a5'
      AND source_package_path='training/roles/nine/1.0.0'
      AND package_tree_git_sha1='0738e13d0ce53a5f1368aa7472e2375fb491a3d9'
      AND manifest_blob_git_sha1='21f81ed20dac38a58c3082c1463a556e7ebf4d53'
  ) THEN RAISE EXCEPTION 'NINE_EXACT_SOURCE_BINDING_MISSING'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM bt2.training_packages
    WHERE agent_key='thirteen' AND version='1.0.0'
      AND source_commit='4de273b3d56ec642c7f9ba83e4767029cf054559'
      AND source_tree='92b69ef1bda00b49807b20b2e9641925677fee33'
      AND source_package_path='training/roles/thirteen/corrections/v1.0.0'
      AND package_tree_git_sha1='3cc36d9aef3f84cbc2d9d808ff3d92d3714faf5e'
      AND manifest_blob_git_sha1='f532dcdb5d812726f433f155f20f8a4f829ee656'
  ) THEN RAISE EXCEPTION 'THIRTEEN_EXACT_SOURCE_BINDING_MISSING'; END IF;

  IF EXISTS (
    SELECT 1 FROM bt2.training_packages
    WHERE status<>'REGISTERED'
       OR source_binding_state<>'BYTE_PRESERVED_VERIFIED'
       OR compatibility_state<>'UNASSESSED'
  ) THEN
    RAISE EXCEPTION 'COMPLETE_FRONTIER_STATE_COLLAPSED';
  END IF;

  IF (SELECT count(*) FROM bt2.training_qualifications)<>0 THEN
    RAISE EXCEPTION 'COMPLETE_FRONTIER_CREATED_QUALIFICATION';
  END IF;
  IF (SELECT count(*) FROM bt2.training_installation_events)<>0 THEN
    RAISE EXCEPTION 'COMPLETE_FRONTIER_CREATED_INSTALLATION';
  END IF;

  IF (SELECT evidence->>'registered_package_count' FROM bt2.migration_receipts WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V3') IS DISTINCT FROM '9' THEN
    RAISE EXCEPTION 'V3_RECEIPT_MUTATED_BY_V4';
  END IF;
  IF (SELECT evidence->>'registered_package_count' FROM bt2.migration_receipts WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V4') IS DISTINCT FROM '13' THEN
    RAISE EXCEPTION 'V4_RECEIPT_NOT_BOUND_TO_13';
  END IF;
END
$test$;

-- Replay only the 9 -> 13 transition. It must converge without rewriting V3.
\ir ../data/0007_remaining_numbered_training_source_registration_v1.sql
\ir ../data/0008_verified_training_source_registry_receipt_v4.sql

DO $test$
BEGIN
  IF (SELECT count(*) FROM bt2.training_packages)<>13 THEN
    RAISE EXCEPTION 'COMPLETE_FRONTIER_REPLAY_NOT_IDEMPOTENT';
  END IF;
  IF (SELECT count(*) FROM bt2.training_packages WHERE agent_key IN ('five','six','nine','thirteen'))<>4 THEN
    RAISE EXCEPTION 'COMPLETE_FRONTIER_REPLAY_SUBJECT_COUNT_MISMATCH';
  END IF;
  IF (SELECT count(*) FROM bt2.migration_receipts WHERE migration_key IN (
      'BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1',
      'BT2-TRAINING-SIX-V1.0.0-BYTE-PRESERVATION-V1',
      'BT2-TRAINING-NINE-V1.0.0-BYTE-PRESERVATION-V1',
      'BT2-TRAINING-THIRTEEN-V1.0.0-BYTE-PRESERVATION-V1'
    ))<>4 THEN
    RAISE EXCEPTION 'COMPLETE_FRONTIER_PRESERVATION_RECEIPT_REPLAY_MISMATCH';
  END IF;
  IF (SELECT count(*) FROM bt2.migration_receipts WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V4')<>1 THEN
    RAISE EXCEPTION 'V4_RECEIPT_REPLAY_DUPLICATED';
  END IF;
  IF (SELECT evidence->>'registered_package_count' FROM bt2.migration_receipts WHERE migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V3') IS DISTINCT FROM '9' THEN
    RAISE EXCEPTION 'V3_RECEIPT_MUTATED_BY_V4_REPLAY';
  END IF;
  IF (SELECT count(*) FROM bt2.training_qualifications)<>0 OR (SELECT count(*) FROM bt2.training_installation_events)<>0 THEN
    RAISE EXCEPTION 'COMPLETE_FRONTIER_REPLAY_CREATED_RUNTIME_EFFECT';
  END IF;
END
$test$;

ROLLBACK;
