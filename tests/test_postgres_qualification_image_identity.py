import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "qualification" / "source_identity.py"
spec = importlib.util.spec_from_file_location("bt2_source_identity_under_test", MODULE_PATH)
source_identity = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(source_identity)


class PostgresQualificationImageIdentityTests(unittest.TestCase):
    def test_forged_prefixed_digest_from_docker_is_rejected(self):
        replies = [
            subprocess.CompletedProcess([], 0, stdout="true\n", stderr=""),
            subprocess.CompletedProcess([], 0, stdout="sha256:imageid\n", stderr=""),
            subprocess.CompletedProcess([], 0, stdout="postgres:16\n", stderr=""),
            subprocess.CompletedProcess(
                [],
                0,
                stdout=json.dumps([{"HostIp": "0.0.0.0", "HostPort": "5432"}]) + "\n",
                stderr="",
            ),
            subprocess.CompletedProcess(
                [],
                0,
                stdout=json.dumps(["postgres@sha256:not-the-image"]) + "\n",
                stderr="",
            ),
        ]
        with patch.object(source_identity.shutil, "which", return_value="/usr/bin/docker"), patch.object(
            source_identity.subprocess, "run", side_effect=replies
        ):
            with self.assertRaisesRegex(SystemExit, "exactly one verified postgres@sha256"):
                source_identity.observe_postgres_container_image(
                    "container-1",
                    "postgresql://postgres:postgres@localhost:5432/bt2_ci",
                )

    def test_database_url_must_target_the_inspected_container_port(self):
        digest = "postgres@sha256:" + "a" * 64
        replies = [
            subprocess.CompletedProcess([], 0, stdout="true\n", stderr=""),
            subprocess.CompletedProcess([], 0, stdout="sha256:imageid\n", stderr=""),
            subprocess.CompletedProcess([], 0, stdout="postgres:16\n", stderr=""),
            subprocess.CompletedProcess(
                [],
                0,
                stdout=json.dumps([{"HostIp": "0.0.0.0", "HostPort": "55432"}]) + "\n",
                stderr="",
            ),
        ]
        with patch.object(source_identity.shutil, "which", return_value="/usr/bin/docker"), patch.object(
            source_identity.subprocess, "run", side_effect=replies
        ):
            with self.assertRaisesRegex(SystemExit, "does not target the inspected PostgreSQL container"):
                source_identity.observe_postgres_container_image(
                    "container-B",
                    "postgresql://postgres:postgres@localhost:5432/bt2_ci",
                )

    def test_verified_docker_digest_is_returned(self):
        digest = "postgres@sha256:" + "a" * 64
        replies = [
            subprocess.CompletedProcess([], 0, stdout="true\n", stderr=""),
            subprocess.CompletedProcess([], 0, stdout="sha256:imageid\n", stderr=""),
            subprocess.CompletedProcess([], 0, stdout="postgres:16\n", stderr=""),
            subprocess.CompletedProcess(
                [],
                0,
                stdout=json.dumps([{"HostIp": "0.0.0.0", "HostPort": "5432"}]) + "\n",
                stderr="",
            ),
            subprocess.CompletedProcess([], 0, stdout=json.dumps([digest]) + "\n", stderr=""),
        ]
        with patch.object(source_identity.shutil, "which", return_value="/usr/bin/docker"), patch.object(
            source_identity.subprocess, "run", side_effect=replies
        ):
            observed = source_identity.observe_postgres_container_image(
                "container-1",
                "postgresql://postgres:postgres@localhost:5432/bt2_ci",
            )
        self.assertEqual(observed["repo_digest"], digest)
        self.assertEqual(observed["verification_method"], "DOCKER_CONTAINER_IMAGE_INSPECT")


if __name__ == "__main__":
    unittest.main()
