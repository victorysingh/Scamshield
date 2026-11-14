"""
test_alert_and_log.py
Tests for tools/alert_and_log.py — all data synthetic.
Uses tmp_path fixture so no real data/ files are written during tests.
"""

import json
from pathlib import Path
from typing import Any

import pytest

import tools.alert_and_log as aal


def _make_result(risk: str, scam_type: str = "bank_kyc") -> dict[str, Any]:
    return {
        "risk": risk,
        "scam_type": scam_type,
        "flagged": risk != "low",
        "signal_count": 2 if risk == "high" else 1,
    }


@pytest.fixture(autouse=True)
def redirect_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect file writes to a temp directory for every test."""
    monkeypatch.setattr(aal, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(aal, "_ALERT_FILE", tmp_path / "alerts.jsonl")
    monkeypatch.setattr(aal, "_LOG_FILE", tmp_path / "cases.jsonl")


class TestAlertTrustedContact:
    def test_high_risk_produces_alert(self, tmp_path: Path) -> None:
        result = aal.alert_trusted_contact(_make_result("high"), "Synth Parent")
        assert result["alerted"] is True
        assert "Synth Parent" in result["message_sent"]
        assert "HIGH-RISK" in result["message_sent"]

    def test_low_risk_no_alert(self, tmp_path: Path) -> None:
        result = aal.alert_trusted_contact(_make_result("low"), "Synth Parent")
        assert result["alerted"] is False
        assert "NO ALERT" in result["message_sent"]

    def test_medium_risk_no_alert(self, tmp_path: Path) -> None:
        result = aal.alert_trusted_contact(_make_result("medium"), "Synth Parent")
        assert result["alerted"] is False

    def test_alert_written_to_file(self, tmp_path: Path) -> None:
        aal.alert_trusted_contact(_make_result("high"), "Synth Parent")
        lines = (tmp_path / "alerts.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["risk"] == "high"
        assert record["alerted"] is True

    def test_multiple_alerts_appended(self, tmp_path: Path) -> None:
        aal.alert_trusted_contact(_make_result("high"), "Synth Parent")
        aal.alert_trusted_contact(_make_result("high"), "Synth Sibling")
        lines = (tmp_path / "alerts.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2

    def test_return_is_valid_json(self, tmp_path: Path) -> None:
        result = aal.alert_trusted_contact(_make_result("high"), "Synth Parent")
        assert json.dumps(result)  # serialisable


class TestLogCase:
    def test_log_writes_record(self, tmp_path: Path) -> None:
        result = aal.log_case("Synthetic scam message", _make_result("high"), label="scam")
        assert result["logged"] is True
        lines = (tmp_path / "cases.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["label"] == "scam"
        assert record["risk"] == "high"

    def test_log_appends_multiple(self, tmp_path: Path) -> None:
        aal.log_case("Msg 1", _make_result("high"), label="scam")
        aal.log_case("Msg 2", _make_result("low"), label="genuine")
        lines = (tmp_path / "cases.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2

    def test_case_id_unique(self, tmp_path: Path) -> None:
        r1 = aal.log_case("Msg A", _make_result("high"), label="scam")
        r2 = aal.log_case("Msg B", _make_result("low"), label="genuine")
        assert r1["case_id"] != r2["case_id"]

    def test_return_is_valid_json(self, tmp_path: Path) -> None:
        result = aal.log_case("Synthetic message", _make_result("medium"), label="scam")
        assert json.dumps(result)

    def test_empty_label_allowed(self, tmp_path: Path) -> None:
        result = aal.log_case("Unknown message", _make_result("low"), label="")
        assert result["label"] == ""
        assert result["logged"] is True
