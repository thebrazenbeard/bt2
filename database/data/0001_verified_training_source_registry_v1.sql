-- BT2 canonical training source registry population V1.
-- Preconditions: corresponding byte-preservation receipts already exist as VERIFIED.
-- This data load registers preserved source only. It does not establish compatibility,
-- qualification, runtime installation, assignment, authority, or currentness.

SELECT bt2.register_preserved_training_package_v1(
  'two','1.0.0','thebrazenbeard/build-team-2.0','two',
  '47f26e2c5c9b37e6fc61134844278d524f095b51','f1599a046c7dd6882a4cfdc8054c21c255441a6a',
  'training/roles/two/v1.0.0',
  'archive/training-sources/build-team-2.0/two/v1.0.0/TRAINING_MANIFEST.yaml',
  'e42eeb5c3c269b8e42aa955b1e85846d63eafe98','257eaeef34c568e1c8812f6e3451a276162b1fac',
  'BT2-TRAINING-TWO-V1.0.0-BYTE-PRESERVATION-V1'
);

SELECT bt2.register_preserved_training_package_v1(
  'three','1.0.0','thebrazenbeard/build-team-2.0','training/three-role-v1.0.0',
  'f5f43e61c85ed96df040c2a2d8e1df523706a215','594d2000ee0cb0f5dcbdc1edf6586430140049c2',
  'training/roles/three/v1.0.0',
  'archive/training-sources/build-team-2.0/three/v1.0.0/TRAINING_MANIFEST.json',
  '696484549f1e729bb04b546e50973efc1fa4439c','315777e08bffc4808ebf68e715c8d58c2d00f2ee',
  'BT2-TRAINING-THREE-V1.0.0-BYTE-PRESERVATION-V1'
);

SELECT bt2.register_preserved_training_package_v1(
  'seven','1.0.0','thebrazenbeard/project-achilles','main',
  'dbf9ceb2391567463d864198405c9b5d1e77db09','1cd715bef0d2a33478d3a635bcc05155c95ab4f9',
  'training/roles/seven/v1.0.0',
  'archive/training-sources/project-achilles/seven/v1.0.0/TRAINING_MANIFEST.json',
  '86b38a66d7bb5d6b71e1bf9754dee3248e2e9792','00e89de1dd4d37e54feb6a75341335c80e878595',
  'BT2-TRAINING-SEVEN-V1.0.0-BYTE-PRESERVATION-V1'
);

SELECT bt2.register_preserved_training_package_v1(
  'eight','1.0.0','thebrazenbeard/build-team-2.0','feature/eight-training-v1.0.0',
  '7fb3f506a66324b5a54d7cda3103899d520c3f04','62fec5e73f39ba6583becc601a352f0892aa60bc',
  'training/roles/eight/v1.0.0',
  'archive/training-sources/build-team-2.0/eight/v1.0.0/TRAINING_MANIFEST.yaml',
  '5217e383cefad53b9ef97f6e35544b0e10f8da58','afb8042a344c01290bfd43685cc05ee489d12462',
  'BT2-TRAINING-EIGHT-V1.0.0-BYTE-PRESERVATION-V1'
);

SELECT bt2.register_preserved_training_package_v1(
  'masa','1.0.0','thebrazenbeard/build-team-2.0','training/masa-v1.0.0',
  'bdfe4e04bdba3dca1661ac7f940e0d7ed0206a8d','7e34b0aca5ab58b5ca5046b694989b158b5fc4ff',
  'training/roles/masa/v1.0.0',
  'archive/training-sources/build-team-2.0/masa/v1.0.0/manifest.json',
  '96f8aa5f37dc8bb72d5ec270bf372e28a5b992a5','6d04c333fea85cbf410b36861211579e16d276a9',
  'BT2-TRAINING-MASA-V1.0.0-BYTE-PRESERVATION-V1'
);

SELECT bt2.register_preserved_training_package_v1(
  'mune','1.0.1','thebrazenbeard/build-team-2.0','training/mune-debugger-verification-v1.0.1',
  '6c84086e217fa4f8a1214eb0d69718e48a96e12d','892c0ea4fd77543fdadd9d19d7c7cc7ac7d91697',
  'training/roles/mune/v1.0.1',
  'archive/training-sources/build-team-2.0/mune/v1.0.1/training-manifest.json',
  '5e8c87021bfda9a6fc44fa121c32410ddc6aedf9','5d2b6cdaa603b60edc860801eaae5dd8644d3c9a',
  'BT2-TRAINING-MUNE-V1.0.1-BYTE-PRESERVATION-V1'
);

SELECT bt2.register_preserved_training_package_v1(
  'hephaestus','1.0.0','thebrazenbeard/build-team-2.0','training/hephaestus-v1.0.0',
  'a3fc622535444e2ef7c3c472d94bee787a7110be','199a8845b8c0698cc228c6d49eb6e57fba87c9d8',
  'training/roles/hephaestus/v1.0.0',
  'archive/training-sources/build-team-2.0/hephaestus/v1.0.0/TRAINING_MANIFEST.yaml',
  'e14ea9f72bbe6e15151f78f3bd617526b22b57fa','22b3418484d8d6ef6a2149bf3ac2b5454595d111',
  'BT2-TRAINING-HEPHAESTUS-V1.0.0-BYTE-PRESERVATION-V1'
);
