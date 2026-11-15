"""
test_classify_and_score.py
Tests for tools/classify_and_score.py — all messages synthetic.
"""

import json
import pytest
from tools.classify_and_score import classify_and_score


def _valid_json(r: dict) -> bool:
    try:
        json.dumps(r)
        return True
    except (TypeError, ValueError):
        return False


class TestScamTypes:
    def test_bank_kyc_detected(self) -> None:
        msg = "Your SynthBank KYC is incomplete. Share your OTP immediately."
        r = classify_and_score(msg)
        assert r["scam_type"] == "bank_kyc"

    def test_courier_customs_detected(self) -> None:
        msg = "Your parcel is held at customs. Pay clearance fee urgently."
        r = classify_and_score(msg)
        assert r["scam_type"] == "courier_customs"

    def test_fake_official_detected(self) -> None:
        msg = "CBI cybercrime department has issued an arrest warrant against your number."
        r = classify_and_score(msg)
        assert r["scam_type"] == "fake_official"

    def test_prize_detected(self) -> None:
        msg = "Congratulations! You have won ₹10,000 in the SynthLotto lucky draw."
        r = classify_and_score(msg)
        assert r["scam_type"] == "prize"

    def test_investment_detected(self) -> None:
        msg = "Guaranteed 40% monthly returns on your investment. Join now!"
        r = classify_and_score(msg)
        assert r["scam_type"] == "investment"

    def test_unknown_for_clean_message(self) -> None:
        msg = "Your SynthBank statement for October is ready."
        r = classify_and_score(msg)
        assert r["scam_type"] == "unknown"


class TestRiskLevels:
    def test_high_risk_on_arrest_threat(self) -> None:
        msg = "Enforcement Directorate: arrest warrant issued against your Aadhaar."
        r = classify_and_score(msg)
        assert r["risk"] == "high"

    def test_high_risk_on_remote_access(self) -> None:
        msg = "Install AnyDesk so our agent can verify your account."
        r = classify_and_score(msg)
        assert r["risk"] == "high"

    def test_high_risk_multiple_signals(self) -> None:
        msg = "URGENT: Share your OTP now or your account will be arrested and frozen."
        r = classify_and_score(msg)
        assert r["risk"] == "high"

    def test_medium_risk_single_signal(self) -> None:
        msg = "Your account KYC needs update at synthbank.in."
        r = classify_and_score(msg)
        assert r["risk"] in ("medium", "low")  # may vary; not high

    def test_low_risk_clean(self) -> None:
        msg = "Your monthly statement is ready. No action needed."
        r = classify_and_score(msg)
        assert r["risk"] == "low"
        assert r["flagged"] is False


class TestReturnContract:
    @pytest.mark.parametrize("msg", [
        "Share OTP now!",
        "Arrest warrant issued.",
        "Your statement is ready.",
        "",
    ])
    def test_always_valid_json(self, msg: str) -> None:
        r = classify_and_score(msg)
        assert _valid_json(r)
        assert "scam_type" in r
        assert "risk" in r
        assert r["risk"] in ("low", "medium", "high")
        assert isinstance(r["signals"], list)
        assert isinstance(r["reasons"], list)

    def test_non_string_input(self) -> None:
        r = classify_and_score(None)  # type: ignore[arg-type]
        assert r["risk"] == "low"
        assert r["flagged"] is False
