# Zmodo -> OpenIPC -> Synology Surveillance Station Repurpose V1

Status: `ACTIVE_RESEARCH / PHYSICAL_IDENTIFICATION_REQUIRED / NO_FLASH_AUTHORITY_INFERRED`

## Objective

Repurpose Patrick's installed Zmodo cameras away from Zmodo software/networking by replacing camera firmware where technically feasible, with the target end state:

`camera hardware -> OpenIPC (or mechanically equivalent open firmware) -> stable H.264 RTSP + preferably ONVIF -> Synology Surveillance Station on DS216`

The Synology NAS is intended to replace the practical recording role of the Zmodo NVR. Reflashing the Zmodo NVR is not a current priority.

## Patrick decision

Patrick explicitly selected firmware replacement rather than a stock-firmware compatibility bridge.

This decision authorizes research, identification, recovery planning, and later device-specific flashing only when a safe recoverable procedure has been established. It does not erase normal precautions against bricking hardware.

## Known inventory

### Synology
- Synology DiskStation DS216.
- Surveillance Station is installed.
- Current Synology licensing should be fresh-checked before final camera-count planning; current public Synology material says NAS systems normally include two default device licenses and additional regular IP cameras generally consume one license each.

### Zmodo
1. One Pivot camera.
   - Historical working identification from the retired terminal: likely `ZM-SHP001B`.
   - Treat as UNVERIFIED until the physical label is read.
   - Do not use as first sacrificial target because PTZ/audio/sensor GPIO integration widens the board-support problem.

2. Amazon ASIN `B01IT8LLQG`.
   - Research identification: `ZM-KW0003-500GB` 720p wireless NVR kit.
   - NVR identity reported in surviving product documentation: `ZM-SS7008D4`.
   - Individual included camera SKU remains unresolved.
   - One fixed camera from this kit is the preferred first reverse-engineering target.

3. Amazon ASIN `B06XCJPZD5`.
   - Exact model remains UNKNOWN from public-index research.
   - Require physical label/FCC/board identification.

4. Amazon ASIN `B078WKHCVK`.
   - Exact model remains UNKNOWN from public-index research.
   - Require physical label/FCC/board identification.

Do not infer identical internals from retail model/family alone. Zmodo and other camera vendors may change SoC, sensor, flash, or Wi-Fi hardware inside the same marketed family.

## External evidence already established

### OpenIPC Zmodo case: ZM-SH75D0001 / ZH-IXY1D
OpenIPC firmware issue #665 documents a Zmodo camera with:
- HiSilicon Hi3518EV100;
- RTL8188EUS USB Wi-Fi;
- no Ethernet and no SD card;
- serial/UART as the practical recovery/control path;
- OpenIPC boot achieved, but Wi-Fi required driver/configuration work.

The issue remained open and had repository activity in 2026.

Implication: successful OpenIPC boot does not guarantee networking. Preserve serial recovery access until the target camera has stable network operation.

### OpenIPC Zmodo case: ZP-IBH15-S
OpenIPC firmware issue #1352 documents:
- HiSilicon Hi3518CV100;
- stock firmware identifying a likely JXH22 sensor;
- OpenIPC boot achieved;
- video pipeline failure due sensor/ISP mismatch or initialization problems.

Implication: successful firmware boot is not success. The success gate is stable sensor capture and encoded stream.

### Current OpenIPC source
Current OpenIPC source contains an `rtl8188eus-openipc` package supporting RTL8188EU/EUS/ETV USB adapters, but package existence does not prove a specific older Hi3518 board/image enables or initializes it correctly.

Search of current OpenIPC firmware/builder/wiki did not locate a Zmodo-specific board profile suitable for blindly flashing Patrick's cameras.

## Success criteria

A converted camera is not considered successful merely because it boots Linux.

Minimum success for Synology use:
1. deterministic boot after power cycle;
2. image sensor initializes correctly;
3. stable H.264 video stream;
4. stable LAN connectivity;
5. RTSP endpoint usable by Surveillance Station;
6. no dependence on Zmodo cloud/app;
7. preserved recovery route and stock backup.

Preferred:
8. ONVIF discovery/control;
9. IR-cut/night mode;
10. usable Wi-Fi where camera lacks Ethernet;
11. audio where hardware/driver support is practical;
12. PTZ only after fixed-camera path is proven.

## Failure classes to expect

- wrong SoC image;
- wrong image sensor driver or sensor clock/address;
- wrong flash geometry/partition map;
- Wi-Fi kernel-module incompatibility;
- board-specific GPIO power/reset requirements for Wi-Fi, IR-cut, LEDs, speaker, microphone, or motors;
- vendor U-Boot environment assumptions;
- inaccessible or locked bootloader;
- bad flash with no network recovery;
- partial success where Linux boots but video or networking does not.

## First-device strategy

Use one fixed camera from the KW0003 kit as the first target.

Do NOT begin with the Pivot unless fixed-camera conversion fails or its hardware proves materially easier.

## Phase A — no-write reconnaissance

Before opening or flashing:

1. Keep the camera on stock firmware.
2. Avoid vendor firmware updates and factory reset until stock firmware has been preserved.
3. If operationally convenient, deny outbound Internet while retaining local LAN/DHCP; this is optional and must not disrupt other household devices.
4. Record external label information:
   - exact model;
   - FCC ID if present;
   - hardware revision;
   - power rating.
   Do not persist serial number, QR provisioning token, Wi-Fi credentials, or device UID in shared project source.
5. Record LAN identity:
   - IP address;
   - MAC/OUI;
   - listening TCP/UDP services;
   - any RTSP/HTTP/vendor service banners.
   Treat local addresses as ephemeral bench evidence, not durable identity.

## Phase B — board identification

Open the same camera and photograph both PCB sides at enough resolution to read:
- SoC;
- SPI NOR/NAND flash part number;
- RAM markings if visible;
- image sensor or sensor daughterboard;
- Wi-Fi chipset/module;
- crystal/oscillator markings if relevant;
- unpopulated headers/test pads;
- silkscreen board revision;
- likely UART pads.

Do not assume UART voltage.

Before attaching an adapter:
1. identify ground;
2. measure idle TX voltage relative to ground;
3. select a logic-level adapter compatible with the measured level;
4. initially connect CAMERA TX -> ADAPTER RX and common GND only;
5. do not connect adapter VCC;
6. power camera from its normal supply.

115200 8N1 is a common first probe, not an assumption. If no coherent boot output appears, test plausible baud rates without transmitting.

## Phase C — stock boot and shell evidence

Capture a complete cold-boot UART log.

Desired evidence:
- SoC;
- U-Boot version;
- boot medium;
- flash geometry;
- partition map;
- kernel version;
- root filesystem;
- sensor initialization;
- Wi-Fi driver/module;
- GPIO setup;
- vendor main process;
- boot interruption method.

If a stock shell is available, use read-only identification first. `ipctool` is preferred when compatible.

## Phase D — recovery before modification

Hard gate: no destructive flash until recoverability exists.

Required:
1. complete stock flash backup, preferably via two independent reads;
2. cryptographic hashes for each read;
3. identical digest or explained difference;
4. saved U-Boot environment;
5. partition boundaries recorded;
6. known method to rewrite stock flash if OpenIPC fails.

Prefer preserving stock U-Boot on the first experiment. Replacing the bootloader is a separate risk and should not be bundled with the first rootfs/kernel test unless technically unavoidable.

If feasible, prefer:
- TFTP/RAM boot;
- temporary kernel/rootfs load;
- or another reversible boot path
before erasing working stock partitions.

## Phase E — OpenIPC decision gate

Only choose an OpenIPC image after exact identification of:
- SoC;
- flash type/size;
- sensor;
- networking chipset;
- board-specific power/reset GPIO requirements where known.

Possible outcomes:
- SUPPORTED_STRAIGHTFORWARD;
- SUPPORTED_CUSTOM_BOARD_CONFIG_REQUIRED;
- BOOTS_BUT_SENSOR_PORT_REQUIRED;
- BOOTS_BUT_NETWORK_DRIVER_WORK_REQUIRED;
- UNSUPPORTED_OR_NOT_WORTH_PORTING.

No cross-flashing between nearby Hi3518 variants merely because filenames look similar.

## Phase F — Synology acceptance

After stable local OpenIPC operation:
1. verify H.264 RTSP with an independent client;
2. enable/configure ONVIF if supported;
3. add camera to Surveillance Station using ONVIF when reliable;
4. otherwise use Synology user-defined RTSP;
5. verify sustained recording, reconnect after camera/NAS reboot, timestamps, night mode, and retention behavior.

Camera detectability by Synology is not the only criterion; stable recording and reconnect behavior are required.

## Historical correction from retired chat

An earlier chat instruction said to use a 3.3 V TTL adapter as the starting assumption. This is superseded by the safer rule above: measure the camera UART level first. 3.3 V is common but must not be presumed.

## Claim ceiling

Current state is:
- research feasibility: POSITIVE;
- exact Patrick camera hardware: NOT YET IDENTIFIED;
- OpenIPC compatibility for Patrick's specific cameras: UNKNOWN;
- stock backup: NOT YET OBTAINED;
- flash performed: NO;
- RTSP/ONVIF from converted Patrick camera: NOT YET OBSERVED;
- Surveillance Station qualification: NOT YET OBSERVED.

## Durable external references

- OpenIPC firmware issue #665: Zmodo ZM-SH75D0001 / ZH-IXY1D, Hi3518EV100 + RTL8188EUS.
- OpenIPC firmware issue #1352: Zmodo ZP-IBH15-S, Hi3518CV100 sensor/ISP failure after OpenIPC flash.
- OpenIPC firmware repository: `OpenIPC/firmware`.
- OpenIPC wiki/install guidance: `OpenIPC/wiki`.
- Synology Surveillance Station: user-defined RTSP / ONVIF capability should be fresh-checked against the installed Surveillance Station version at integration time.

## Next runnable frontier

Physical access is the real prerequisite.

At the bench, collect in this order:
1. external label/FCC photos;
2. local network inventory;
3. full PCB photos;
4. receive-only UART cold-boot log;
5. stock shell/ipctool evidence if available;
6. complete stock flash dump + hashes.

Only then select or build firmware.

## Coordination

Future persistent interface: `BT2 Coordinator`.

An appropriate embedded/hardware worker may be instantiated from durable BT2 state in a temporary execution runtime. Seven may be instantiated independently for hostile recovery/brick-risk review if useful. Neither requires a permanent ChatGPT conversation.
