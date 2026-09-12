-- Register Four v1.0.1 as the ninth preserved/unassessed training source.
-- Preconditions are independently verified exact Git tree identity on One's source-preservation frontier.
-- This step creates a preservation receipt and source registration only.
-- It does not establish compatibility, qualification, BASE_READY, installation, activation,
-- assignment, authority, or currentness.

DO $receipt$
DECLARE
  v_digest constant text := 'b024cd062133d37821c17094bf6001b5ff9c4b164cd58e5ca43a3499d28ca1b1';
  v_existing record;
BEGIN
  SELECT migration_digest_sha256,result_state,evidence
  INTO v_existing
  FROM bt2.migration_receipts
  WHERE migration_key='BT2-TRAINING-FOUR-V1.0.1-BYTE-PRESERVATION-V1';

  IF FOUND THEN
    IF v_existing.migration_digest_sha256 IS DISTINCT FROM v_digest
       OR v_existing.result_state <> 'VERIFIED'
       OR v_existing.evidence->>'source_package_tree' IS DISTINCT FROM '0953afaeeec7543697f97711e5a2326d954e9fa3'
       OR v_existing.evidence->>'target_package_tree' IS DISTINCT FROM '0953afaeeec7543697f97711e5a2326d954e9fa3' THEN
      RAISE EXCEPTION 'FOUR_PRESERVATION_RECEIPT_CONFLICT';
    END IF;
  ELSE
    INSERT INTO bt2.migration_receipts(
      migration_key,source_system,target_component,migration_digest_sha256,
      result_state,evidence,applied_at,verified_at
    ) VALUES(
      'BT2-TRAINING-FOUR-V1.0.1-BYTE-PRESERVATION-V1',
      'GITHUB:thebrazenbeard/build-team-2.0',
      'GITHUB:thebrazenbeard/bt2:archive/training-sources/build-team-2.0/four/v1.0.1',
      v_digest,
      'VERIFIED',
      jsonb_build_object(
        'agent_key','four',
        'training_version','1.0.1',
        'source_ref','main',
        'source_commit','bf045dd627aef5650b9ed85c036b9a6340afe68f',
        'source_commit_tree','889e388fe4ccc76cba7d49a5c5707e7cda56c4ce',
        'source_package_path','training/roles/four/1.0.1',
        'source_package_tree','0953afaeeec7543697f97711e5a2326d954e9fa3',
        'manifest_blob','25c89bc947edf1e09470e567f2f5f193cb928333',
        'source_set_digest_sha256','1070866d342043c21d06d9bc384fbf7cf78d231850ef2edef514b3e95229c332',
        'target_branch','work/source-preservation-v1',
        'preservation_commit','3a9ad076771d43653bc4ea5f9664d724c2ae02f4',
        'frontier_commit','5fdca5acab589b2ede6199f531192ff123d3d27e',
        'target_package_path','archive/training-sources/build-team-2.0/four/v1.0.1',
        'target_package_tree','0953afaeeec7543697f97711e5a2326d954e9fa3',
        'verification_method','EXACT_GIT_TREE_IDENTITY_INDEPENDENTLY_REPRODUCED_BY_TWO',
        'qualification_effect','NONE',
        'runtime_installation_effect','NONE',
        'authority_effect','NONE'
      ),
      clock_timestamp(),clock_timestamp()
    );
  END IF;
END
$receipt$;

SELECT bt2.register_preserved_training_package_v1(
  'four','1.0.1','thebrazenbeard/build-team-2.0','main',
  'bf045dd627aef5650b9ed85c036b9a6340afe68f','889e388fe4ccc76cba7d49a5c5707e7cda56c4ce',
  'training/roles/four/1.0.1',
  'archive/training-sources/build-team-2.0/four/v1.0.1/training_manifest.json',
  '0953afaeeec7543697f97711e5a2326d954e9fa3','25c89bc947edf1e09470e567f2f5f193cb928333',
  'BT2-TRAINING-FOUR-V1.0.1-BYTE-PRESERVATION-V1',
  NULL,
  '1070866d342043c21d06d9bc384fbf7cf78d231850ef2edef514b3e95229c332'
);
