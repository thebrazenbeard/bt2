# Public main-head VS Code task exposure manifest — 2026-10-24

**Read-only source snapshot.** Only 78 public repositories owned by `thebrazenbeard` were enumerated through the connected GitHub inventory (public-visibility filter). Each `main` HEAD was resolved using read-only `git ls-remote ... refs/heads/main` and `.vscode/tasks.json` was fetched from that **exact immutable commit** using GitHub's file API. This freezes the *source snapshot* without claiming that main remains unchanged afterward. No private names, counts, or metadata are included here.

**Result: 45/78 source matches**: variant A = 41; variant B = 4. Other observations: 26 task files have nonmatching blob identities with no hidden `folderOpen` Node-command pattern; 7 repositories returned 404 for the task file at the pinned commit. Among the 45 matches, all 45 referenced font-path assets were present at the same pinned commits. Neither tasks nor assets were executed. This is conditional editor-startup **exposure in repository source**, not evidence of VS Code consent, workstation execution, infection, or actual runtime effect.

- **Variant A:** task blob `de6de3adea989c8e85a4d39ce0337378d92be7db` references a concealed Node invocation of a font-named `.lkf` file; referenced asset blob `31ce18eddf4c96c1a705dbceaec4304f953d4dc3` (41 repositories).
- **Variant B:** task blob `1a828db96e870c5db15b61f9e82f515cbb26f4c3` references a concealed Node invocation of a font-named `.woff2` file; referenced asset blob `60e613b9bcbd179b2c27b96c2130cd7db2e4250b` (4 repositories).
- **Classification:** exact suspect Git-blob SHAs were cross-checked against content markers for hidden task, `runOn: folderOpen`, and a Node command. The task files use permissive JSONC syntax (trailing comma), so plain strict JSON parsing is not an appropriate test. Other task blobs did not contain the same three markers; this bounded scan does **not** rule out unrelated autoexecution mechanisms elsewhere in source.
- **Claim ceiling:** `SOURCE` only; `INSTALL`, `RUNTIME`, host impact, and `E2E` are **UNKNOWN**.

| Public repository | Exact `main` HEAD SHA | `.vscode/tasks.json` blob SHA | Classification |
| --- | --- | --- | --- |
| [`abil`](https://github.com/thebrazenbeard/abil) | `c842c9058d8a4d1e4caf4bf7cdfad7e3c678ce6b` | — | Task file absent |
| [`achilles`](https://github.com/thebrazenbeard/achilles) | `6dc9c3ab4d3fbad968a4cfd06f9c80c6b918fff4` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`Attune`](https://github.com/thebrazenbeard/Attune) | `5e14cf9e296e5630f6929715801e5d76114eb866` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`axle`](https://github.com/thebrazenbeard/axle) | `66e2af93440db6ea3e52a149b1ba9f28e5d6c228` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`blotter`](https://github.com/thebrazenbeard/blotter) | `2493b354488cefe4a3f0d2b80372b93c6b1cfeb4` | — | Task file absent |
| [`bt2`](https://github.com/thebrazenbeard/bt2) | `ba830cc2914813c3b4e76751f77b1cf3a132a5c4` | `658bd8f40eb95318425e87ab9cf2b343da6b5d11` | No matching task |
| [`bugops`](https://github.com/thebrazenbeard/bugops) | `1d35bcbd16da24c7635a004845de1390de850b4e` | — | Task file absent |
| [`build-team-2.0`](https://github.com/thebrazenbeard/build-team-2.0) | `950112a697550b689049da807f2d8176a507c38f` | — | Task file absent |
| [`ccb-core`](https://github.com/thebrazenbeard/ccb-core) | `9d53ce2e624b406f6661f92b26087a83a4e84997` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`conations`](https://github.com/thebrazenbeard/conations) | `8380724e9e85641f2ef3250819cb625a03549c8b` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`cricket`](https://github.com/thebrazenbeard/cricket) | `1d50d789d0276b708d7d13d735fd7a8b08f13ce2` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`deepmemorystorage`](https://github.com/thebrazenbeard/deepmemorystorage) | `63edbc51fb87c889ab58051d02e18ba2aeca0d24` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`discovery`](https://github.com/thebrazenbeard/discovery) | `628e5f26a00f7547347d14db32f1df2da5cdf193` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`driftguard`](https://github.com/thebrazenbeard/driftguard) | `4b94e1f86827609a46c1c41178964c6996de7fcb` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`ears`](https://github.com/thebrazenbeard/ears) | `3eb2ba7b836a42ae8c9bed0f966c5cf18fad4cc3` | `1a828db96e870c5db15b61f9e82f515cbb26f4c3` | B (suspect) |
| [`empathy`](https://github.com/thebrazenbeard/empathy) | `72000cfed9c272c3a9b59f562f691e3354a112a3` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`executor`](https://github.com/thebrazenbeard/executor) | `d630f0c634baf4ee63237ce0aab89a5b3b1d97de` | `21ce1e26e4a35fca5d3dcd439958863af23be631` | No matching task |
| [`fuckup`](https://github.com/thebrazenbeard/fuckup) | `850fe1ce40bd68992b9cf3a531af078200e0c7a0` | `21ce1e26e4a35fca5d3dcd439958863af23be631` | No matching task |
| [`god-brain`](https://github.com/thebrazenbeard/god-brain) | `e22c95c263a053827f6c9eaf865cf291272b25b9` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`hc-brain`](https://github.com/thebrazenbeard/hc-brain) | `e1d1a790535d25a01645e285f614a73a48511869` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`hephaestus`](https://github.com/thebrazenbeard/hephaestus) | `5bfe7b6036b5b9b6f0fd6a3722dcbb155386288d` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`humility`](https://github.com/thebrazenbeard/humility) | `d3b58e6b45fc45d6fe6041b3e36d2b60f5697f9b` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`ingest`](https://github.com/thebrazenbeard/ingest) | `8c77610781a4d9c598651a681253f26d3832c437` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`intranel`](https://github.com/thebrazenbeard/intranel) | `25a2332a9e2bbd476f7001b9e11062e9f39f32bd` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`lgcm`](https://github.com/thebrazenbeard/lgcm) | `7c04a57baadaeeddf5beb49b29454080308179c7` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`lou-pole`](https://github.com/thebrazenbeard/lou-pole) | `04f63752c4ad408b3421d22e12f084d56dfe3ac5` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`masamune`](https://github.com/thebrazenbeard/masamune) | `a7be73fe0d946edc35a6d646cd49dda2fe790c5b` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`mediaphile-client`](https://github.com/thebrazenbeard/mediaphile-client) | `985b29916991a9fc2e2742a0e5479536e6d2f482` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`mediaphile-server`](https://github.com/thebrazenbeard/mediaphile-server) | `bc41d563ad3c9cc27e5f12e6859d25454186b9b6` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`meso-crct`](https://github.com/thebrazenbeard/meso-crct) | `ea309b932b64d804d5e1472b18a0b48a5ff9fd8f` | `658bd8f40eb95318425e87ab9cf2b343da6b5d11` | No matching task |
| [`meta`](https://github.com/thebrazenbeard/meta) | `5855181033205cc3faef47f3c4133aa3dbbe2b44` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`model-training`](https://github.com/thebrazenbeard/model-training) | `5822b4d3f9836c46d5f4140ddfabafb9eb569d24` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`mosaic`](https://github.com/thebrazenbeard/mosaic) | `276282a1d4a34588f34a4d18ab3da76a84b6e48b` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`naijin-ryu`](https://github.com/thebrazenbeard/naijin-ryu) | `f2ebfce34dd81dde5ef8977d885bd0f92ffe5664` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`noema`](https://github.com/thebrazenbeard/noema) | `6886594db65a26f873ba58436f34c3f1d4db7d01` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`ocd`](https://github.com/thebrazenbeard/ocd) | `18b36b89eaf0985494a1046b01a3ef7a5b69a443` | `1a828db96e870c5db15b61f9e82f515cbb26f4c3` | B (suspect) |
| [`on-theo`](https://github.com/thebrazenbeard/on-theo) | `5a86bc1949c01dfc4b20df55a026e26763287100` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`personification`](https://github.com/thebrazenbeard/personification) | `6ff4b4c168f900b14989dfddc53df087577dbb4d` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`physica`](https://github.com/thebrazenbeard/physica) | `8569716575569e1acff952771edd9debc2fde4df` | `21ce1e26e4a35fca5d3dcd439958863af23be631` | No matching task |
| [`portal`](https://github.com/thebrazenbeard/portal) | `6b601b8b291bd59cd79bcc1a96befab50ec2ebda` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`pre-active`](https://github.com/thebrazenbeard/pre-active) | `bd4d575e117de146173e183ee12ce4256ac02132` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`project-lantern`](https://github.com/thebrazenbeard/project-lantern) | `cc78ebfcddc194d208dcc1a62cb5f70c915e3996` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`project-runner`](https://github.com/thebrazenbeard/project-runner) | `e0ef7ebdacf4344d8635ceb5039155164494d7c8` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`RepairTracker`](https://github.com/thebrazenbeard/RepairTracker) | `52bc48885e0179f46cc01d0db87774cc87d8cf4a` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`rezon`](https://github.com/thebrazenbeard/rezon) | `d27da3cab31ae96aff3c65385fc31354dc8aeb8c` | `21ce1e26e4a35fca5d3dcd439958863af23be631` | No matching task |
| [`roots`](https://github.com/thebrazenbeard/roots) | `87c66782382906f085cc75205c8d800a07f2fe25` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`RSLinux`](https://github.com/thebrazenbeard/RSLinux) | `700fe39124115b9f78d9be85cdc72194b737ecd9` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`self`](https://github.com/thebrazenbeard/self) | `02c689a2480f7c13cbd2a09693049062d9afbe46` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`semanticatlas`](https://github.com/thebrazenbeard/semanticatlas) | `8c516a5673c4c2c16d78c921d6c4c0cdf36a0ee6` | `21ce1e26e4a35fca5d3dcd439958863af23be631` | No matching task |
| [`semiotics`](https://github.com/thebrazenbeard/semiotics) | `9daf947ffea0d31c198ba7a9c61f7aab434677d0` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`spk-packager`](https://github.com/thebrazenbeard/spk-packager) | `6dad804195931040998b89feda439d02611461d8` | `1a828db96e870c5db15b61f9e82f515cbb26f4c3` | B (suspect) |
| [`spm`](https://github.com/thebrazenbeard/spm) | `670e22a107fe85f3d50ba8d58a6eb38c4a190e3c` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`sql-connectome`](https://github.com/thebrazenbeard/sql-connectome) | `d02c99c632945cdf1228fdc8518e1c9a47aa2a7d` | `21ce1e26e4a35fca5d3dcd439958863af23be631` | No matching task |
| [`t-kal-in-ket`](https://github.com/thebrazenbeard/t-kal-in-ket) | `b0af150c2405b519fd921bac33e5f9f1f35f92d7` | — | Task file absent |
| [`tattler`](https://github.com/thebrazenbeard/tattler) | `685f343abb2d684dedfdaa9e0d32a5a39441a506` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`temporal`](https://github.com/thebrazenbeard/temporal) | `7f38e00e79500d1c976e9e6be7fd7211477c4a09` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`testament`](https://github.com/thebrazenbeard/testament) | `1580b49cadb6be424aabb42b7c460f757c26c00f` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`thebrazenbeard`](https://github.com/thebrazenbeard/thebrazenbeard) | `649be13988f7f897caeac98b2fe6b699e501c145` | `1a828db96e870c5db15b61f9e82f515cbb26f4c3` | B (suspect) |
| [`transcendence`](https://github.com/thebrazenbeard/transcendence) | `69bc900010f9a64a9c8d4423d2a9cff824d82ed2` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`unbound-sol`](https://github.com/thebrazenbeard/unbound-sol) | `6b0172a423dcefb636036419eb14d0a4dac7e278` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`unvtrslr`](https://github.com/thebrazenbeard/unvtrslr) | `a8290ac7ebbb62d9b777021c0f1e12401e579695` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`v-e-r-a`](https://github.com/thebrazenbeard/v-e-r-a) | `9fab8e4123c653bc12054c56196c15cd48999997` | — | Task file absent |
| [`vera`](https://github.com/thebrazenbeard/vera) | `3a4b1999aee8a0da5f61153eda5c23487f667c0e` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`vera-ark`](https://github.com/thebrazenbeard/vera-ark) | `b2876c5bbb6cba95801797555960680d431bd6ad` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`vera-control-plane`](https://github.com/thebrazenbeard/vera-control-plane) | `0654b4a646f2168b672f4f78cef71e33bc79d643` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`vera-habitat`](https://github.com/thebrazenbeard/vera-habitat) | `f99f59b4c61e5ff4f864d46674433d3831d624b5` | `658bd8f40eb95318425e87ab9cf2b343da6b5d11` | No matching task |
| [`vera-mesh`](https://github.com/thebrazenbeard/vera-mesh) | `3242f72a0c4b9cb53679563c78f66528841296f5` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`vera-mono`](https://github.com/thebrazenbeard/vera-mono) | `64c4a756a8c4d6fc791787de80303f7ee0f64869` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`vera-R9A0`](https://github.com/thebrazenbeard/vera-R9A0) | `80379b7b6caeebb610debf572f50fd9f4f378563` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`vera-synology`](https://github.com/thebrazenbeard/vera-synology) | `7ea68b921979ed9b8aaec07094da9254b42626d0` | — | Task file absent |
| [`vision`](https://github.com/thebrazenbeard/vision) | `145afa827b3d89426f07f55b1b370c072aff62db` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`volition`](https://github.com/thebrazenbeard/volition) | `d43c16c15577157335a9251ba43e45dd96dfcdf4` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`voss`](https://github.com/thebrazenbeard/voss) | `cbc86d114da52ad1aa59db0fa1916f7895a805f3` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`wip`](https://github.com/thebrazenbeard/wip) | `13185463f2221e25d474f8a17ecef1c10a877dea` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`workbridge`](https://github.com/thebrazenbeard/workbridge) | `e3f748ccc7701eaf5a6e16fe0905a32bbff014ac` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |
| [`workbridgecommander`](https://github.com/thebrazenbeard/workbridgecommander) | `40e523f75771a83b4be666940c6fdec3f8ffe445` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`WorkBridgeMCP`](https://github.com/thebrazenbeard/WorkBridgeMCP) | `3efd1b3d53de8909b141b4cd33aaae3273f81634` | `513d537675b8bdb691aee22a24862745c3edd595` | No matching task |
| [`world-zero`](https://github.com/thebrazenbeard/world-zero) | `bd414f9844f4e48786f1b27b15be8e661913cb18` | `de6de3adea989c8e85a4d39ce0337378d92be7db` | A (suspect) |

