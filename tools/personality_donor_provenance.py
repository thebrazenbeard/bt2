"""Fail-closed donor and redistributable companion evidence for BT2 personas.

These pinned bytes identify upstream inputs; they do not prove model quality,
downstream contributor permissions, or release-level license compliance.
"""

from __future__ import annotations

from pathlib import Path
import shutil

from identity_coding_models import ROOT, require
from train_identity_lora_pilot import sha256_file


DONOR_REPO = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
DONOR_REVISION = "2e1fd397ee46e1388853d2af2c993145b0f1098a"
DONOR_WEIGHTS_SHA256 = "c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8"
DONOR_LICENSE_SHA256 = "832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e"
LICENSE_COMPANION = "LICENSE.Qwen2.5-Coder-1.5B-Instruct"
NOTICE_COMPANION = "BT2_PERSONALITY_MODIFICATION_NOTICE.md"
NOTICE_SOURCE = "coding_models/training/THIRD_PARTY_MODEL_NOTICE.md"
UPSTREAM_LICENSE_SOURCE = "coding_models/training/upstream/Qwen2.5-Coder-1.5B-Instruct_LICENSE"


def verify_donor_identity(base: Path, weights_sha256: str,
                          receipt: object | None = None,
                          *, bt2: Path = ROOT) -> dict[str, str]:
    """Pin weights/revision attribution and vendored 11,343-byte upstream license.

    Revision is supported by the official HF blob/resolve URLs and their
    repository commit headers; a local folder is not itself a Git checkout.
    """
    require(weights_sha256 == DONOR_WEIGHTS_SHA256,
            "donor weight digest is not the pinned Qwen revision")
    license_file = bt2 / UPSTREAM_LICENSE_SOURCE
    require(license_file.is_file() and not license_file.is_symlink(),
            "pinned upstream Apache-2.0 license is missing from BT2 source")
    require(sha256_file(license_file) == DONOR_LICENSE_SHA256,
            "bundled HF donor LICENSE differs from pinned upstream Apache-2.0 bytes")
    # Local HF snapshots may omit LICENSE. If present, it cannot contradict
    # the exact upstream file. The verified BT2 source provides the companion.
    local_license = base / "LICENSE"
    if local_license.exists() or local_license.is_symlink():
        require(local_license.is_file() and not local_license.is_symlink() and
                sha256_file(local_license) == DONOR_LICENSE_SHA256,
                "local HF donor LICENSE contradicts pinned upstream license")
    result = {"repo_id": DONOR_REPO, "repo_revision": DONOR_REVISION,
              "weights_sha256": DONOR_WEIGHTS_SHA256,
              "license_sha256": DONOR_LICENSE_SHA256}
    if receipt is not None:
        require(isinstance(receipt, dict) and receipt == result,
                "missing or altered pinned donor provenance receipt")
    return result


def copy_attribution_companions(*, base: Path, bt2: Path,
                                output: Path, provenance: dict[str, str]) -> dict[str, str]:
    """Copy verified license and BT2 change notice beside a new derivative.

    Destination must already be new and contain no companion targets; never
    overwrite any existing license, notice, GGUF, or model directory.
    """
    verify_donor_identity(base, provenance.get("weights_sha256", ""),
                          provenance, bt2=bt2)
    require(output.is_dir() and not output.is_symlink(),
            "new derivative destination must exist as a regular directory")
    source_notice = bt2 / NOTICE_SOURCE
    require(source_notice.is_file() and not source_notice.is_symlink(),
            "missing source-bound model modification notice")
    require(DONOR_REVISION in source_notice.read_text(encoding="utf-8") and
            DONOR_REPO in source_notice.read_text(encoding="utf-8"),
            "notice lacks pinned upstream provenance")
    files = ((bt2 / UPSTREAM_LICENSE_SOURCE, output / LICENSE_COMPANION),
             (source_notice, output / NOTICE_COMPANION))
    for _src, dest in files:
        require(not dest.exists() and not dest.is_symlink(),
                "refusing to overwrite existing donor attribution companion")
    # Input hashes are reverified after copying to reject source drift.
    for src, dest in files:
        with dest.open("xb") as writer, src.open("rb") as reader:
            shutil.copyfileobj(reader, writer)
    require(sha256_file(bt2 / UPSTREAM_LICENSE_SOURCE) == DONOR_LICENSE_SHA256 and
            sha256_file(output / LICENSE_COMPANION) == DONOR_LICENSE_SHA256,
            "upstream license drifted during companion packaging")
    require(sha256_file(source_notice) == sha256_file(output / NOTICE_COMPANION),
            "model modification notice drifted during companion packaging")
    return {LICENSE_COMPANION: DONOR_LICENSE_SHA256,
            NOTICE_COMPANION: sha256_file(output / NOTICE_COMPANION)}
