-- BT2 training preservation provenance binding V1.
-- Forward-only repair for issue #31.
-- Historical preservation receipts remain immutable. This migration adds a
-- normalized, source-controlled provenance subject keyed by preservation receipt
-- migration_key and requires verified training registrations to match it exactly.
--
-- This establishes provenance binding only. It does not establish compatibility,
-- qualification, installation, activation, assignment, authority, or currentness.

CREATE TABLE bt2.training_preservation_provenance_bindings_v1 (
  preservation_migration_key text PRIMARY KEY,
  agent_key text NOT NULL,
  version text NOT NULL,
  source_repository text NOT NULL,
  source_ref text NOT NULL,
  source_commit text NOT NULL,
  source_tree text NOT NULL,
  source_package_path text NOT NULL,
  target_manifest_path text NOT NULL,
  package_tree_git_sha1 text NOT NULL,
  manifest_blob_git_sha1 text NOT NULL,
  provenance_digest_sha256 text NOT NULL,
  evidence_class text NOT NULL DEFAULT 'SOURCE_CONTROLLED_RECONCILED_PRESERVATION_PROVENANCE_V1',
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  CONSTRAINT training_preservation_binding_source_commit_sha1_check
    CHECK (source_commit ~ '^[0-9a-f]{40}$'),
  CONSTRAINT training_preservation_binding_source_tree_sha1_check
    CHECK (source_tree ~ '^[0-9a-f]{40}$'),
  CONSTRAINT training_preservation_binding_package_tree_sha1_check
    CHECK (package_tree_git_sha1 ~ '^[0-9a-f]{40}$'),
  CONSTRAINT training_preservation_binding_manifest_blob_sha1_check
    CHECK (manifest_blob_git_sha1 ~ '^[0-9a-f]{40}$'),
  CONSTRAINT training_preservation_binding_digest_sha256_check
    CHECK (provenance_digest_sha256 ~ '^[0-9a-f]{64}$'),
  CONSTRAINT training_preservation_binding_package_identity_uniq
    UNIQUE (agent_key,version,package_tree_git_sha1)
);

CREATE OR REPLACE FUNCTION bt2.training_preservation_provenance_digest_v1(
  p_agent_key text,
  p_version text,
  p_source_repository text,
  p_source_ref text,
  p_source_commit text,
  p_source_tree text,
  p_source_package_path text,
  p_target_manifest_path text,
  p_package_tree_git_sha1 text,
  p_manifest_blob_git_sha1 text
) RETURNS text
LANGUAGE sql
IMMUTABLE
STRICT
AS $function$
  SELECT encode(
    public.digest(
      convert_to(
        jsonb_build_array(
          p_agent_key,p_version,p_source_repository,p_source_ref,p_source_commit,
          p_source_tree,p_source_package_path,p_target_manifest_path,
          lower(p_package_tree_git_sha1),lower(p_manifest_blob_git_sha1)
        )::text,
        'UTF8'
      ),
      'sha256'
    ),
    'hex'
  )
$function$;

ALTER TABLE bt2.training_preservation_provenance_bindings_v1
  ADD CONSTRAINT training_preservation_binding_digest_matches_tuple_check
  CHECK (
    provenance_digest_sha256 = bt2.training_preservation_provenance_digest_v1(
      agent_key,version,source_repository,source_ref,source_commit,source_tree,
      source_package_path,target_manifest_path,package_tree_git_sha1,manifest_blob_git_sha1
    )
  );

INSERT INTO bt2.training_preservation_provenance_bindings_v1(
  preservation_migration_key,agent_key,version,source_repository,source_ref,
  source_commit,source_tree,source_package_path,target_manifest_path,
  package_tree_git_sha1,manifest_blob_git_sha1,provenance_digest_sha256
)
SELECT
  v.preservation_migration_key,v.agent_key,v.version,v.source_repository,v.source_ref,
  v.source_commit,v.source_tree,v.source_package_path,v.target_manifest_path,
  lower(v.package_tree_git_sha1),lower(v.manifest_blob_git_sha1),
  bt2.training_preservation_provenance_digest_v1(
    v.agent_key,v.version,v.source_repository,v.source_ref,v.source_commit,v.source_tree,
    v.source_package_path,v.target_manifest_path,v.package_tree_git_sha1,v.manifest_blob_git_sha1
  )
FROM (VALUES
  ('BT2-TRAINING-ONE-V1.0.0-BYTE-PRESERVATION-V1','one','1.0.0','thebrazenbeard/build-team-2.0','training/one-role-v1.0.0','ed1f2c5515425deab4c77c2f4fd291a1086191d4','0cd6bca8a3d1aaab9e47f3f8b23d3a18a6f4d40a','training/roles/one/v1.0.0','archive/training-sources/build-team-2.0/one/v1.0.0/TRAINING_MANIFEST.yaml','e27ce67b67159fb445347ae9a8888fe3c480cdd1','e6d8e6b4a8139d8073b08fe7f346107f66a16458'),
  ('BT2-TRAINING-TWO-V1.0.0-BYTE-PRESERVATION-V1','two','1.0.0','thebrazenbeard/build-team-2.0','two','47f26e2c5c9b37e6fc61134844278d524f095b51','f1599a046c7dd6882a4cfdc8054c21c255441a6a','training/roles/two/v1.0.0','archive/training-sources/build-team-2.0/two/v1.0.0/TRAINING_MANIFEST.yaml','e42eeb5c3c269b8e42aa955b1e85846d63eafe98','257eaeef34c568e1c8812f6e3451a276162b1fac'),
  ('BT2-TRAINING-THREE-V1.0.0-BYTE-PRESERVATION-V1','three','1.0.0','thebrazenbeard/build-team-2.0','training/three-role-v1.0.0','f5f43e61c85ed96df040c2a2d8e1df523706a215','594d2000ee0cb0f5dcbdc1edf6586430140049c2','training/roles/three/v1.0.0','archive/training-sources/build-team-2.0/three/v1.0.0/TRAINING_MANIFEST.json','696484549f1e729bb04b546e50973efc1fa4439c','315777e08bffc4808ebf68e715c8d58c2d00f2ee'),
  ('BT2-TRAINING-SEVEN-V1.0.0-BYTE-PRESERVATION-V1','seven','1.0.0','thebrazenbeard/project-achilles','main','dbf9ceb2391567463d864198405c9b5d1e77db09','1cd715bef0d2a33478d3a635bcc05155c95ab4f9','training/roles/seven/v1.0.0','archive/training-sources/project-achilles/seven/v1.0.0/TRAINING_MANIFEST.json','86b38a66d7bb5d6b71e1bf9754dee3248e2e9792','00e89de1dd4d37e54feb6a75341335c80e878595'),
  ('BT2-TRAINING-EIGHT-V1.0.0-BYTE-PRESERVATION-V1','eight','1.0.0','thebrazenbeard/build-team-2.0','feature/eight-training-v1.0.0','7fb3f506a66324b5a54d7cda3103899d520c3f04','62fec5e73f39ba6583becc601a352f0892aa60bc','training/roles/eight/v1.0.0','archive/training-sources/build-team-2.0/eight/v1.0.0/TRAINING_MANIFEST.yaml','5217e383cefad53b9ef97f6e35544b0e10f8da58','afb8042a344c01290bfd43685cc05ee489d12462'),
  ('BT2-TRAINING-MASA-V1.0.0-BYTE-PRESERVATION-V1','masa','1.0.0','thebrazenbeard/build-team-2.0','training/masa-v1.0.0','bdfe4e04bdba3dca1661ac7f940e0d7ed0206a8d','7e34b0aca5ab58b5ca5046b694989b158b5fc4ff','training/roles/masa/v1.0.0','archive/training-sources/build-team-2.0/masa/v1.0.0/manifest.json','96f8aa5f37dc8bb72d5ec270bf372e28a5b992a5','6d04c333fea85cbf410b36861211579e16d276a9'),
  ('BT2-TRAINING-MUNE-V1.0.1-BYTE-PRESERVATION-V1','mune','1.0.1','thebrazenbeard/build-team-2.0','training/mune-debugger-verification-v1.0.1','6c84086e217fa4f8a1214eb0d69718e48a96e12d','892c0ea4fd77543fdadd9d19d7c7cc7ac7d91697','training/roles/mune/v1.0.1','archive/training-sources/build-team-2.0/mune/v1.0.1/training-manifest.json','5e8c87021bfda9a6fc44fa121c32410ddc6aedf9','5d2b6cdaa603b60edc860801eaae5dd8644d3c9a'),
  ('BT2-TRAINING-HEPHAESTUS-V1.0.0-BYTE-PRESERVATION-V1','hephaestus','1.0.0','thebrazenbeard/build-team-2.0','training/hephaestus-v1.0.0','a3fc622535444e2ef7c3c472d94bee787a7110be','199a8845b8c0698cc228c6d49eb6e57fba87c9d8','training/roles/hephaestus/v1.0.0','archive/training-sources/build-team-2.0/hephaestus/v1.0.0/TRAINING_MANIFEST.yaml','e14ea9f72bbe6e15151f78f3bd617526b22b57fa','22b3418484d8d6ef6a2149bf3ac2b5454595d111'),
  ('BT2-TRAINING-FOUR-V1.0.1-BYTE-PRESERVATION-V1','four','1.0.1','thebrazenbeard/build-team-2.0','main','bf045dd627aef5650b9ed85c036b9a6340afe68f','889e388fe4ccc76cba7d49a5c5707e7cda56c4ce','training/roles/four/1.0.1','archive/training-sources/build-team-2.0/four/v1.0.1/training_manifest.json','0953afaeeec7543697f97711e5a2326d954e9fa3','25c89bc947edf1e09470e567f2f5f193cb928333'),
  ('BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1','five','1.0.0','thebrazenbeard/build-team-2.0','main','da419ea83323c54908380c6ad57d65ea2c580f14','912f329cf1f780171827a64b7bc8ce65512a1efa','training/roles/five/v1.0.0','archive/training-sources/build-team-2.0/five/v1.0.0/manifest.yaml','f6c962e81c75deab3aa55d300fc4f9f9fa89f034','124db5b0aca892f05506d0a7086c8d9a2c9cd83f'),
  ('BT2-TRAINING-SIX-V1.0.0-BYTE-PRESERVATION-V1','six','1.0.0','thebrazenbeard/build-team-2.0','main','fcb358b0e7ca7b1b57cf868e34aac28d5c0e55c4','333adfc841c25e3e9a407f6c666ed2b7d51a402b','training/roles/six/v1.0.0','archive/training-sources/build-team-2.0/six/v1.0.0/TRAINING_MANIFEST.json','ba3ffa8adc18f635e516356a92e7d0450fa7a789','bc6906f8dd5c41712fea3691c167b14a39ffd7b9'),
  ('BT2-TRAINING-NINE-V1.0.0-BYTE-PRESERVATION-V1','nine','1.0.0','thebrazenbeard/build-team-2.0','main','a25c05f6c475dc96eb1c72900432ab4e74cb5acd','faf7501b8f93aeca2346b3848131d7386f6c86a5','training/roles/nine/1.0.0','archive/training-sources/build-team-2.0/nine/v1.0.0/training_manifest.json','0738e13d0ce53a5f1368aa7472e2375fb491a3d9','21f81ed20dac38a58c3082c1463a556e7ebf4d53'),
  ('BT2-TRAINING-THIRTEEN-V1.0.0-BYTE-PRESERVATION-V1','thirteen','1.0.0','thebrazenbeard/build-team-2.0','main','4de273b3d56ec642c7f9ba83e4767029cf054559','92b69ef1bda00b49807b20b2e9641925677fee33','training/roles/thirteen/corrections/v1.0.0','archive/training-sources/build-team-2.0/thirteen/corrections/v1.0.0/manifest.yaml','3cc36d9aef3f84cbc2d9d808ff3d92d3714faf5e','f532dcdb5d812726f433f155f20f8a4f829ee656')
) AS v(
  preservation_migration_key,agent_key,version,source_repository,source_ref,
  source_commit,source_tree,source_package_path,target_manifest_path,
  package_tree_git_sha1,manifest_blob_git_sha1
);

CREATE OR REPLACE FUNCTION bt2.reject_training_preservation_binding_mutation_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
BEGIN
  RAISE EXCEPTION 'TRAINING_PRESERVATION_PROVENANCE_BINDINGS_ARE_IMMUTABLE';
END
$function$;

CREATE TRIGGER training_preservation_provenance_bindings_no_update_delete_v1
BEFORE UPDATE OR DELETE ON bt2.training_preservation_provenance_bindings_v1
FOR EACH ROW EXECUTE FUNCTION bt2.reject_training_preservation_binding_mutation_v1();

REVOKE INSERT,UPDATE,DELETE,TRUNCATE
ON bt2.training_preservation_provenance_bindings_v1
FROM PUBLIC;

CREATE OR REPLACE FUNCTION bt2.guard_training_package_source_binding_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
DECLARE
  v_receipt record;
  v_binding bt2.training_preservation_provenance_bindings_v1%ROWTYPE;
  v_receipt_tree text;
BEGIN
  IF NEW.source_binding_state = 'BYTE_PRESERVED_VERIFIED' THEN
    IF NEW.preservation_receipt_id IS NULL THEN
      RAISE EXCEPTION 'BYTE_PRESERVATION_REQUIRES_RECEIPT';
    END IF;

    SELECT mr.migration_key,mr.result_state,mr.evidence
    INTO STRICT v_receipt
    FROM bt2.migration_receipts mr
    WHERE mr.migration_receipt_id=NEW.preservation_receipt_id;

    IF v_receipt.result_state <> 'VERIFIED' THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_NOT_VERIFIED';
    END IF;

    SELECT b.*
    INTO STRICT v_binding
    FROM bt2.training_preservation_provenance_bindings_v1 b
    WHERE b.preservation_migration_key=v_receipt.migration_key;

    v_receipt_tree:=COALESCE(
      v_receipt.evidence->>'target_package_tree',
      v_receipt.evidence->>'source_package_tree'
    );

    IF v_receipt_tree IS NULL
       OR lower(v_receipt_tree) IS DISTINCT FROM lower(v_binding.package_tree_git_sha1)
       OR lower(NEW.package_tree_git_sha1) IS DISTINCT FROM lower(v_binding.package_tree_git_sha1) THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_PACKAGE_TREE_MISMATCH';
    END IF;

    IF v_receipt.evidence->>'qualification_effect' IS DISTINCT FROM 'NONE' THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_QUALIFICATION_EFFECT_NOT_NONE';
    END IF;

    IF v_receipt.evidence->>'runtime_installation_effect' IS DISTINCT FROM 'NONE' THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_RUNTIME_EFFECT_NOT_NONE';
    END IF;

    IF NEW.agent_key IS DISTINCT FROM v_binding.agent_key THEN
      RAISE EXCEPTION 'PRESERVATION_PROVENANCE_MISMATCH:agent_key';
    ELSIF NEW.version IS DISTINCT FROM v_binding.version THEN
      RAISE EXCEPTION 'PRESERVATION_PROVENANCE_MISMATCH:version';
    ELSIF NEW.source_repository IS DISTINCT FROM v_binding.source_repository THEN
      RAISE EXCEPTION 'PRESERVATION_PROVENANCE_MISMATCH:source_repository';
    ELSIF NEW.source_ref IS DISTINCT FROM v_binding.source_ref THEN
      RAISE EXCEPTION 'PRESERVATION_PROVENANCE_MISMATCH:source_ref';
    ELSIF NEW.source_commit IS DISTINCT FROM v_binding.source_commit THEN
      RAISE EXCEPTION 'PRESERVATION_PROVENANCE_MISMATCH:source_commit';
    ELSIF NEW.source_tree IS DISTINCT FROM v_binding.source_tree THEN
      RAISE EXCEPTION 'PRESERVATION_PROVENANCE_MISMATCH:source_tree';
    ELSIF NEW.source_package_path IS DISTINCT FROM v_binding.source_package_path THEN
      RAISE EXCEPTION 'PRESERVATION_PROVENANCE_MISMATCH:source_package_path';
    ELSIF NEW.manifest_path IS DISTINCT FROM v_binding.target_manifest_path THEN
      RAISE EXCEPTION 'PRESERVATION_PROVENANCE_MISMATCH:manifest_path';
    ELSIF lower(NEW.manifest_blob_git_sha1) IS DISTINCT FROM lower(v_binding.manifest_blob_git_sha1) THEN
      RAISE EXCEPTION 'PRESERVATION_PROVENANCE_MISMATCH:manifest_blob_git_sha1';
    END IF;

    -- Richer receipts already carry parts of the normalized tuple. If present,
    -- those historical fields must not contradict the canonical binding.
    IF v_receipt.evidence ? 'agent_key'
       AND v_receipt.evidence->>'agent_key' IS DISTINCT FROM v_binding.agent_key THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_PROVENANCE_CONTRADICTION:agent_key';
    END IF;
    IF v_receipt.evidence ? 'training_version'
       AND v_receipt.evidence->>'training_version' IS DISTINCT FROM v_binding.version THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_PROVENANCE_CONTRADICTION:training_version';
    END IF;
    IF v_receipt.evidence ? 'source_ref'
       AND v_receipt.evidence->>'source_ref' IS DISTINCT FROM v_binding.source_ref THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_PROVENANCE_CONTRADICTION:source_ref';
    END IF;
    IF v_receipt.evidence ? 'source_commit'
       AND v_receipt.evidence->>'source_commit' IS DISTINCT FROM v_binding.source_commit THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_PROVENANCE_CONTRADICTION:source_commit';
    END IF;
    IF v_receipt.evidence ? 'source_commit_tree'
       AND v_receipt.evidence->>'source_commit_tree' IS DISTINCT FROM v_binding.source_tree THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_PROVENANCE_CONTRADICTION:source_commit_tree';
    END IF;
    IF v_receipt.evidence ? 'source_package_path'
       AND v_receipt.evidence->>'source_package_path' IS DISTINCT FROM v_binding.source_package_path THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_PROVENANCE_CONTRADICTION:source_package_path';
    END IF;
    IF v_receipt.evidence ? 'manifest_blob'
       AND lower(v_receipt.evidence->>'manifest_blob') IS DISTINCT FROM lower(v_binding.manifest_blob_git_sha1) THEN
      RAISE EXCEPTION 'PRESERVATION_RECEIPT_PROVENANCE_CONTRADICTION:manifest_blob';
    END IF;
  END IF;

  RETURN NEW;
END
$function$;

DROP TRIGGER IF EXISTS training_packages_source_binding_guard_v1
ON bt2.training_packages;

CREATE TRIGGER training_packages_source_binding_guard_v1
BEFORE INSERT OR UPDATE OF
  agent_key,version,source_repository,source_ref,source_commit,source_tree,
  source_package_path,manifest_path,package_tree_git_sha1,manifest_blob_git_sha1,
  preservation_receipt_id,source_binding_state
ON bt2.training_packages
FOR EACH ROW EXECUTE FUNCTION bt2.guard_training_package_source_binding_v1();
