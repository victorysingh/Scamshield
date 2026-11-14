"""
test_explain_in_language.py
Tests for tools/explain_in_language.py — all data synthetic.
"""

import json
import pytest
from tools.explain_in_language import explain_in_language


def _make_result(risk: str, scam_type: str) -> dict:
    return {"risk": risk, "scam_type": scam_type, "flagged": risk != "low"}


def _valid_json(r: dict) -> bool:
    try:
        json.dumps(r)
        return True
    except (TypeError, ValueError):
        return False


class TestEnglish:
    def test_high_risk_english(self) -> None:
        r = explain_in_language(_make_result("high", "bank_kyc"), "english")
        assert r["language"] == "english"
        assert "scam" in r["verdict"].lower() or "⚠️" in r["verdict"]
        assert len(r["instruction"]) > 10

    def test_medium_risk_english(self) -> None:
        r = explain_in_language(_make_result("medium", "prize"), "english")
        assert "suspicious" in r["verdict"].lower() or "⚠️" in r["verdict"]

    def test_low_risk_english(self) -> None:
        r = explain_in_language(_make_result("low", "unknown"), "english")
        assert "genuine" in r["verdict"].lower() or "✅" in r["verdict"]

    def test_instruction_per_scam_type(self) -> None:
        for scam_type in ("bank_kyc", "courier_customs", "fake_official", "prize", "investment", "unknown"):
            r = explain_in_language(_make_result("high", scam_type), "english")
            assert len(r["instruction"]) > 5, f"Empty instruction for {scam_type}"


class TestKannada:
    def test_high_risk_kannada(self) -> None:
        r = explain_in_language(_make_result("high", "fake_official"), "kannada")
        assert r["language"] == "kannada"
        # Kannada verdict contains Kannada characters (Unicode block U+0C80–U+0CFF)
        assert any("\u0C80" <= ch <= "\u0CFF" for ch in r["verdict"])

    def test_medium_risk_kannada(self) -> None:
        r = explain_in_language(_make_result("medium", "investment"), "kannada")
        assert any("\u0C80" <= ch <= "\u0CFF" for ch in r["verdict"])

    def test_instruction_kannada(self) -> None:
        r = explain_in_language(_make_result("high", "bank_kyc"), "kannada")
        assert any("\u0C80" <= ch <= "\u0CFF" for ch in r["instruction"])

    def test_case_insensitive_language(self) -> None:
        r = explain_in_language(_make_result("high", "prize"), "Kannada")
        assert r["language"] == "kannada"


class TestEdgeCases:
    def test_unknown_language_falls_back_to_english(self) -> None:
        r = explain_in_language(_make_result("high", "bank_kyc"), "french")
        assert r["language"] == "english"

    def test_invalid_result_dict(self) -> None:
        r = explain_in_language("not a dict", "english")  # type: ignore[arg-type]
        assert r["verdict"] != ""

    def test_echoes_risk_and_scam_type(self) -> None:
        r = explain_in_language(_make_result("medium", "courier_customs"), "english")
        assert r["risk"] == "medium"
        assert r["scam_type"] == "courier_customs"


class TestReturnContract:
    @pytest.mark.parametrize("lang", ["english", "kannada"])
    @pytest.mark.parametrize("risk", ["low", "medium", "high"])
    def test_always_valid_json(self, lang: str, risk: str) -> None:
        r = explain_in_language(_make_result(risk, "bank_kyc"), lang)
        assert _valid_json(r)
        assert "verdict" in r
        assert "instruction" in r
