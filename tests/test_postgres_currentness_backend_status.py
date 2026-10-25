from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "runtime" / "CURRENTNESS_BACKEND_STATUS_V1.json"


def test_currentness_backend_is_explicitly_unbound_after_wowsql_retirement():
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    assert data["schema"] == "BT2_CURRENTNESS_BACKEND_STATUS_V1"
    assert data["wowsql"]["currentness_role"] == "RETIRED"
    assert data["active_currentness_backend"] is None
    assert data["replacement_currentness_backend"] == "NOT_ESTABLISHED"
    assert data["lantern_currentness"] == "UNKNOWN"
    assert data["rules"]["do_not_query_retired_wowsql_for_currentness"] is True
    assert data["rules"]["do_not_infer_replacement_backend"] is True


def test_v4_candidate_source_is_not_promoted_to_active_backend():
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    assert data["candidate_source_contract"] == "POSTGRESQL_SQL_CONNECTOME_V4"
    assert data["candidate_contract_state"] == "SOURCE_ONLY_NOT_ACTIVE_CURRENTNESS_BACKEND"
    assert data["rules"]["candidate_source_presence_does_not_establish_runtime"] is True
    assert data["evidence_ceiling"] == "SOURCE_STATE_ONLY_NO_RUNTIME_READ_PERFORMED"
