-- Register Five, Six, Nine, and Thirteen as preserved/unassessed training sources.
-- Preconditions: exact byte-preservation evidence exists on One's source-preservation lane.
-- Effect ceiling: source preservation receipt + REGISTERED/BYTE_PRESERVED_VERIFIED/UNASSESSED only.
-- No compatibility, qualification, installation, activation, assignment, authority, or currentness effect.
-- Receipt digest rule used here:
-- SHA256(agent|version|source_commit|source_package_tree|target_package_tree|source_set_digest).

DO $five$
DECLARE
  v_digest constant text := 'ab2c93072f9276e8a64530a497c68405292e9cbd24b74fe6029f32a110090157';
  v_existing record;
BEGIN
  SELECT migration_digest_sha256,result_state,evidence INTO v_existing
  FROM bt2.migration_receipts
  WHERE migration_key='BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1';

  IF FOUND THEN
    IF v_existing.migration_digest_sha256 IS DISTINCT FROM v_digest
       OR v_existing.result_state <> 'VERIFIED'
       OR v_existing.evidence->>'source_package_tree' IS DISTINCT FROM 'f6c962e81c75deab3aa55d300fc4f9f9fa89f034'
       OR v_existing.evidence->>'target_package_tree' IS DISTINCT FROM 'f6c962e81c75deab3aa55d300fc4f9f9fa89f034' THEN
      RAISE EXCEPTION 'FIVE_PRESERVATION_RECEIPT_CONFLICT';
    END IF;
  ELSE
    INSERT INTO bt2.migration_receipts(
      migration_key,source_system,target_component,migration_digest_sha256,
      result_state,evidence,applied_at,verified_at
    ) VALUES(
      'BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1',
      'GITHUB:thebrazenbeard/build-team-2.0',
      'GITHUB:thebrazenbeard/bt2:archive/training-sources/build-team-2.0/five/v1.0.0',
      v_digest,'VERIFIED',
      jsonb_build_object(
        'agent_key','five','training_version','1.0.0','source_ref','main',
        'source_commit','da419ea83323c54908380c6ad57d65ea2c580f14',
        'source_commit_tree','912f329cf1f780171827a64b7bc8ce65512a1efa',
        'source_package_path','training/roles/five/v1.0.0',
        'source_package_tree','f6c962e81c75deab3aa55d300fc4f9f9fa89f034',
        'manifest_blob','124db5b0aca892f05506d0a7086c8d9a2c9cd83f',
        'manifest_digest_sha256','164ee92a70f6585dece59dca09ab84bd6020a4d950393b127091aed91713687c',
        'source_set_digest_sha256','80d2aab944ee8c8e13b83ae99aacc4ba530bc42cda69ed6c9ab21958a64e55f8',
        'preservation_commit','06debec806abc285d628ca5a448366ec8e12b0f1',
        'frontier_commit','c347942b03688298995f06ffa7ca9f4195a52cbb',
        'target_package_path','archive/training-sources/build-team-2.0/five/v1.0.0',
        'target_package_tree','f6c962e81c75deab3aa55d300fc4f9f9fa89f034',
        'verification_method','EXACT_GIT_TREE_IDENTITY_BY_ONE',
        'qualification_effect','NONE','runtime_installation_effect','NONE','authority_effect','NONE'
      ),clock_timestamp(),clock_timestamp()
    );
  END IF;
END
$five$;

SELECT bt2.register_preserved_training_package_v1(
  'five','1.0.0','thebrazenbeard/build-team-2.0','main',
  'da419ea83323c54908380c6ad57d65ea2c580f14','912f329cf1f780171827a64b7bc8ce65512a1efa',
  'training/roles/five/v1.0.0',
  'archive/training-sources/build-team-2.0/five/v1.0.0/manifest.yaml',
  'f6c962e81c75deab3aa55d300fc4f9f9fa89f034','124db5b0aca892f05506d0a7086c8d9a2c9cd83f',
  'BT2-TRAINING-FIVE-V1.0.0-BYTE-PRESERVATION-V1',
  '164ee92a70f6585dece59dca09ab84bd6020a4d950393b127091aed91713687c',
  '80d2aab944ee8c8e13b83ae99aacc4ba530bc42cda69ed6c9ab21958a64e55f8'
);

DO $six$
DECLARE
  v_digest constant text := 'bb430c4fb5d460211170a1b591e39eb4baac27434094d34a5db83c4c807fec69';
  v_existing record;
BEGIN
  SELECT migration_digest_sha256,result_state,evidence INTO v_existing
  FROM bt2.migration_receipts
  WHERE migration_key='BT2-TRAINING-SIX-V1.0.0-BYTE-PRESERVATION-V1';

  IF FOUND THEN
    IF v_existing.migration_digest_sha256 IS DISTINCT FROM v_digest
       OR v_existing.result_state <> 'VERIFIED'
       OR v_existing.evidence->>'source_package_tree' IS DISTINCT FROM 'ba3ffa8adc18f635e516356a92e7d0450fa7a789'
       OR v_existing.evidence->>'target_package_tree' IS DISTINCT FROM 'ba3ffa8adc18f635e516356a92e7d0450fa7a789' THEN
      RAISE EXCEPTION 'SIX_PRESERVATION_RECEIPT_CONFLICT';
    END IF;
  ELSE
    INSERT INTO bt2.migration_receipts(
      migration_key,source_system,target_component,migration_digest_sha256,
      result_state,evidence,applied_at,verified_at
    ) VALUES(
      'BT2-TRAINING-SIX-V1.0.0-BYTE-PRESERVATION-V1',
      'GITHUB:thebrazenbeard/build-team-2.0',
      'GITHUB:thebrazenbeard/bt2:archive/training-sources/build-team-2.0/six/v1.0.0',
      v_digest,'VERIFIED',
      jsonb_build_object(
        'agent_key','six','training_version','1.0.0','source_ref','main',
        'source_commit','fcb358b0e7ca7b1b57cf868e34aac28d5c0e55c4',
        'source_commit_tree','333adfc841c25e3e9a407f6c666ed2b7d51a402b',
        'source_package_path','training/roles/six/v1.0.0',
        'source_package_tree','ba3ffa8adc18f635e516356a92e7d0450fa7a789',
        'manifest_blob','bc6906f8dd5c41712fea3691c167b14a39ffd7b9',
        'manifest_digest_sha256','32ed842c8bb6c2ccc49bb327189da9b03178b403f05ad6b10cca9b5f1ceeff38',
        'source_set_digest_sha256','ef44176582819750193c7d591e9ee449ea8c3d6743a8bff3eb5228baf4fad1cc',
        'preservation_commit','6f751ef53d4909c7c4f71ed2ad74608f202505a0',
        'frontier_commit','c347942b03688298995f06ffa7ca9f4195a52cbb',
        'target_package_path','archive/training-sources/build-team-2.0/six/v1.0.0',
        'target_package_tree','ba3ffa8adc18f635e516356a92e7d0450fa7a789',
        'verification_method','EXACT_GIT_TREE_IDENTITY_BY_ONE',
        'qualification_effect','NONE','runtime_installation_effect','NONE','authority_effect','NONE'
      ),clock_timestamp(),clock_timestamp()
    );
  END IF;
END
$six$;

SELECT bt2.register_preserved_training_package_v1(
  'six','1.0.0','thebrazenbeard/build-team-2.0','main',
  'fcb358b0e7ca7b1b57cf868e34aac28d5c0e55c4','333adfc841c25e3e9a407f6c666ed2b7d51a402b',
  'training/roles/six/v1.0.0',
  'archive/training-sources/build-team-2.0/six/v1.0.0/TRAINING_MANIFEST.json',
  'ba3ffa8adc18f635e516356a92e7d0450fa7a789','bc6906f8dd5c41712fea3691c167b14a39ffd7b9',
  'BT2-TRAINING-SIX-V1.0.0-BYTE-PRESERVATION-V1',
  '32ed842c8bb6c2ccc49bb327189da9b03178b403f05ad6b10cca9b5f1ceeff38',
  'ef44176582819750193c7d591e9ee449ea8c3d6743a8bff3eb5228baf4fad1cc'
);

DO $nine$
DECLARE
  v_digest constant text := 'd91a184e2d1ee6736db0d7447aff7fd8655c58439a458dedc0678eddfb4dc0c7';
  v_existing record;
BEGIN
  SELECT migration_digest_sha256,result_state,evidence INTO v_existing
  FROM bt2.migration_receipts
  WHERE migration_key='BT2-TRAINING-NINE-V1.0.0-BYTE-PRESERVATION-V1';

  IF FOUND THEN
    IF v_existing.migration_digest_sha256 IS DISTINCT FROM v_digest
       OR v_existing.result_state <> 'VERIFIED'
       OR v_existing.evidence->>'source_package_tree' IS DISTINCT FROM '0738e13d0ce53a5f1368aa7472e2375fb491a3d9'
       OR v_existing.evidence->>'target_package_tree' IS DISTINCT FROM '0738e13d0ce53a5f1368aa7472e2375fb491a3d9' THEN
      RAISE EXCEPTION 'NINE_PRESERVATION_RECEIPT_CONFLICT';
    END IF;
  ELSE
    INSERT INTO bt2.migration_receipts(
      migration_key,source_system,target_component,migration_digest_sha256,
      result_state,evidence,applied_at,verified_at
    ) VALUES(
      'BT2-TRAINING-NINE-V1.0.0-BYTE-PRESERVATION-V1',
      'GITHUB:thebrazenbeard/build-team-2.0',
      'GITHUB:thebrazenbeard/bt2:archive/training-sources/build-team-2.0/nine/v1.0.0',
      v_digest,'VERIFIED',
      jsonb_build_object(
        'agent_key','nine','training_version','1.0.0','source_ref','main',
        'source_commit','a25c05f6c475dc96eb1c72900432ab4e74cb5acd',
        'source_commit_tree','faf7501b8f93aeca2346b3848131d7386f6c86a5',
        'source_package_path','training/roles/nine/1.0.0',
        'source_package_tree','0738e13d0ce53a5f1368aa7472e2375fb491a3d9',
        'manifest_blob','21f81ed20dac38a58c3082c1463a556e7ebf4d53',
        'manifest_digest_sha256','a0702c71cd14521cf88312ee9f07c6bf5ccb5a95079b047332e33a532f32e67b',
        'source_set_digest_sha256','bcbee02e5e7f59b763ba1a441a66c4e3b83210befcb85ab7f66a5d0ccf7769e7',
        'preservation_commit','6ca9c42b53c91d64efe2ab726c8515c1f6ef1e4d',
        'frontier_commit','c347942b03688298995f06ffa7ca9f4195a52cbb',
        'target_package_path','archive/training-sources/build-team-2.0/nine/v1.0.0',
        'target_package_tree','0738e13d0ce53a5f1368aa7472e2375fb491a3d9',
        'verification_method','EXACT_GIT_TREE_IDENTITY_INDEPENDENTLY_REESTABLISHED_BY_ONE',
        'qualification_effect','NONE','runtime_installation_effect','NONE','authority_effect','NONE'
      ),clock_timestamp(),clock_timestamp()
    );
  END IF;
END
$nine$;

SELECT bt2.register_preserved_training_package_v1(
  'nine','1.0.0','thebrazenbeard/build-team-2.0','main',
  'a25c05f6c475dc96eb1c72900432ab4e74cb5acd','faf7501b8f93aeca2346b3848131d7386f6c86a5',
  'training/roles/nine/1.0.0',
  'archive/training-sources/build-team-2.0/nine/v1.0.0/training_manifest.json',
  '0738e13d0ce53a5f1368aa7472e2375fb491a3d9','21f81ed20dac38a58c3082c1463a556e7ebf4d53',
  'BT2-TRAINING-NINE-V1.0.0-BYTE-PRESERVATION-V1',
  'a0702c71cd14521cf88312ee9f07c6bf5ccb5a95079b047332e33a532f32e67b',
  'bcbee02e5e7f59b763ba1a441a66c4e3b83210befcb85ab7f66a5d0ccf7769e7'
);

DO $thirteen$
DECLARE
  v_digest constant text := 'b7335f5539cb56ea15033be66d94f7ef32d118f7103ddc0eeba717f54a416b1b';
  v_existing record;
BEGIN
  SELECT migration_digest_sha256,result_state,evidence INTO v_existing
  FROM bt2.migration_receipts
  WHERE migration_key='BT2-TRAINING-THIRTEEN-V1.0.0-BYTE-PRESERVATION-V1';

  IF FOUND THEN
    IF v_existing.migration_digest_sha256 IS DISTINCT FROM v_digest
       OR v_existing.result_state <> 'VERIFIED'
       OR v_existing.evidence->>'source_package_tree' IS DISTINCT FROM '3cc36d9aef3f84cbc2d9d808ff3d92d3714faf5e'
       OR v_existing.evidence->>'target_package_tree' IS DISTINCT FROM '3cc36d9aef3f84cbc2d9d808ff3d92d3714faf5e' THEN
      RAISE EXCEPTION 'THIRTEEN_PRESERVATION_RECEIPT_CONFLICT';
    END IF;
  ELSE
    INSERT INTO bt2.migration_receipts(
      migration_key,source_system,target_component,migration_digest_sha256,
      result_state,evidence,applied_at,verified_at
    ) VALUES(
      'BT2-TRAINING-THIRTEEN-V1.0.0-BYTE-PRESERVATION-V1',
      'GITHUB:thebrazenbeard/build-team-2.0',
      'GITHUB:thebrazenbeard/bt2:archive/training-sources/build-team-2.0/thirteen/corrections/v1.0.0',
      v_digest,'VERIFIED',
      jsonb_build_object(
        'agent_key','thirteen','training_version','1.0.0','source_ref','main',
        'source_commit','4de273b3d56ec642c7f9ba83e4767029cf054559',
        'source_commit_tree','92b69ef1bda00b49807b20b2e9641925677fee33',
        'source_package_path','training/roles/thirteen/corrections/v1.0.0',
        'source_package_tree','3cc36d9aef3f84cbc2d9d808ff3d92d3714faf5e',
        'manifest_blob','f532dcdb5d812726f433f155f20f8a4f829ee656',
        'manifest_digest_sha256','49ca83e55940caecf6df56170bcd5ddca8044933d56db897fbfe0f052c87fc3e',
        'source_set_digest_sha256','89f3da76b9033c9302e2ddb85c68b6bf0b7856383d7bce65f671170d4a8a7bc1',
        'preservation_commit','8176d4a6e5225f84f04dfd51517451f185e6c763',
        'frontier_commit','c347942b03688298995f06ffa7ca9f4195a52cbb',
        'target_package_path','archive/training-sources/build-team-2.0/thirteen/corrections/v1.0.0',
        'target_package_tree','3cc36d9aef3f84cbc2d9d808ff3d92d3714faf5e',
        'verification_method','EXACT_GIT_TREE_IDENTITY_BY_ONE',
        'qualification_effect','NONE','runtime_installation_effect','NONE','authority_effect','NONE'
      ),clock_timestamp(),clock_timestamp()
    );
  END IF;
END
$thirteen$;

SELECT bt2.register_preserved_training_package_v1(
  'thirteen','1.0.0','thebrazenbeard/build-team-2.0','main',
  '4de273b3d56ec642c7f9ba83e4767029cf054559','92b69ef1bda00b49807b20b2e9641925677fee33',
  'training/roles/thirteen/corrections/v1.0.0',
  'archive/training-sources/build-team-2.0/thirteen/corrections/v1.0.0/manifest.yaml',
  '3cc36d9aef3f84cbc2d9d808ff3d92d3714faf5e','f532dcdb5d812726f433f155f20f8a4f829ee656',
  'BT2-TRAINING-THIRTEEN-V1.0.0-BYTE-PRESERVATION-V1',
  '49ca83e55940caecf6df56170bcd5ddca8044933d56db897fbfe0f052c87fc3e',
  '89f3da76b9033c9302e2ddb85c68b6bf0b7856383d7bce65f671170d4a8a7bc1'
);
