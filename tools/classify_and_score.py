"""
classify_and_score.py
Combines red-flag signal counts with keyword heuristics to produce:
  - scam_type : str  (bank_kyc | courier_customs | fake_official |
                       prize | investment | unknown)
  - risk      : str  (low | medium | high)
  - reasons   : list[str]

No live model call required — pure rule-based so it works offline.
When a watsonx.ai key is available, the stub at the bottom can be
replaced with a real Granite inference call.
"""

from typing import Any
import re

from tools.check_red_flags import check_red_flags

# ---------------------------------------------------------------------------
# Scam-type keyword sets  (all lowercase for matching)
# ---------------------------------------------------------------------------

_TYPE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "bank_kyc",
        re.compile(
            r"\b(kyc|know your customer|account (suspend|block|freeze|verif)|"
            r"bank(ing)? (details|update|verif)|re-?verif|aadhar|pan card|"
            r"credit card|debit card|net ?banking|upi|ifsc)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "courier_customs",
        re.compile(
            r"\b(parcel|package|courier|customs|delivery (held|stopped|seized)|"
            r"shipment|clearance fee|dhl|fedex|india post|speed post)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "fake_official",
        re.compile(
            r"\b(cbi|enforcement directorate|income tax|trai|doj|department of "
            r"justice|government of india|supreme court|high court|police|fir|"
            r"iec|ministry|officer|official notice)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "prize",
        re.compile(
            r"\b(won|winner|congratulations|lucky draw|lottery|prize|reward|"
            r"gift card|voucher|cash prize|selected|claim (your )?prize)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "investment",
        re.compile(
            r"\b(invest(ment)?|returns?|profit|guaranteed|doubl(e|ing)|crypto|"
            r"trading|scheme|portfolio|fixed (return|deposit)|mutual fund scam|"
            r"ponzi|high return)\b",
            re.IGNORECASE,
        ),
    ),
]


def _detect_scam_type(message: str) -> str:
    """Return the first matching scam type, or 'unknown'."""
    for scam_type, pattern in _TYPE_PATTERNS:
        if pattern.search(message):
            return scam_type
    return "unknown"


def _compute_risk(signal_count: int, scam_type: str) -> str:
    """
    Map signal count + scam type to low / medium / high.

    Rules (conservative — errs toward higher risk for safety):
      0 signals                       → low
      1 signal                        → medium
      2+ signals                      → high
      Any arrest/remote-access signal → always high (checked by caller)

    A single signal with no recognised scam type used to escalate to high,
    which fired family alerts on ordinary messages; medium still flags it.
    """
    if signal_count == 0:
        return "low"
    if signal_count == 1:
        return "medium"
    return "high"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_and_score(message: str) -> dict[str, Any]:
    """
    Analyse *message* and return scam type, risk level and reasons.

    Parameters
    ----------
    message : str
        Raw text of the message to analyse.

    Returns
    -------
    dict with keys:
        scam_type  (str)        – one of the 6 type labels
        risk       (str)        – low | medium | high
        flagged    (bool)       – True if any red flag found
        signals    (list[dict]) – from check_red_flags
        reasons    (list[str])  – human-readable explanation lines
        signal_count (int)
    """
    if not isinstance(message, str):
        return {
            "scam_type": "unknown",
            "risk": "low",
            "flagged": False,
            "signals": [],
            "reasons": [],
            "signal_count": 0,
        }

    flags = check_red_flags(message)
    signal_names: list[str] = [s["name"] for s in flags["signals"]]
    signal_count: int = flags["count"]

    scam_type = _detect_scam_type(message)

    # Escalate to high if high-severity signals present regardless of count
    high_severity = {"arrest_or_seizure_threat", "remote_access_request"}
    if high_severity.intersection(signal_names):
        risk = "high"
    else:
        risk = _compute_risk(signal_count, scam_type)

    reasons: list[str] = [s["reason"] for s in flags["signals"]]
    if scam_type != "unknown":
        reasons.insert(0, f"Message matches the '{scam_type}' scam pattern.")

    return {
        "scam_type": scam_type,
        "risk": risk,
        "flagged": flags["flagged"],
        "signals": flags["signals"],
        "reasons": reasons,
        "signal_count": signal_count,
    }


# ---------------------------------------------------------------------------
# Stub: replace with real watsonx.ai Granite call when API key is available
# ---------------------------------------------------------------------------
# from ibm_watsonx_ai import APIClient, Credentials
# from ibm_watsonx_ai.foundation_models import ModelInference
# import os
#
# def _granite_classify(message: str) -> dict[str, Any]:
#     client = APIClient(Credentials(
#         url=os.environ["WATSONX_URL"],
#         api_key=os.environ["WATSONX_API_KEY"],
#     ))
#     model = ModelInference(
#         model_id="ibm/granite-3-8b-instruct",
#         api_client=client,
#         project_id=os.environ["WATSONX_PROJECT_ID"],
#     )
#     prompt = f"""Classify this message as a scam or genuine.
# Types: bank_kyc, courier_customs, fake_official, prize, investment, genuine
# Risk: low, medium, high
# Message: {message}
# Respond in JSON: {{"scam_type": "...", "risk": "..."}}"""
#     response = model.generate_text(prompt=prompt)
#     return response  # parse JSON from response text
