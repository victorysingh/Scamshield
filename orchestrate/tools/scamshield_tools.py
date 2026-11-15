"""
orchestrate/tools/scamshield_tools.py

ScamShield tool functions exposed to watsonx Orchestrate via the ADK @tool decorator.
Each function is a thin wrapper around the core tools in tools/.

Rules:
- Full type hints on every parameter and return value.
- Returns plain JSON (dict) — Orchestrate reads this directly.
- No real personal data. No credentials hard-coded.
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

# Make sure the project root is on sys.path when ADK imports this file.
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tools.classify_and_score import classify_and_score as _classify
from tools.explain_in_language import explain_in_language as _explain
from tools.alert_and_log import alert_trusted_contact as _alert, log_case as _log


# ---------------------------------------------------------------------------
# Tool 1: analyse_message
# One call that runs classify_and_score and explain_in_language together.
# This is the primary tool the agent calls first.
# ---------------------------------------------------------------------------

@tool(
    name="analyse_message",
    description=(
        "Analyse a suspicious text message for scam signals. "
        "Returns the scam type, risk level (low/medium/high), "
        "signals detected, and a plain-language explanation in the chosen language."
    ),
    permission=ToolPermission.READ_ONLY,
)
def analyse_message(
    message: str,
    language: str = "english",
) -> dict:
    """
    Analyse a text message and return a full scam verdict with explanation.

    Parameters
    ----------
    message : str
        The raw text of the suspicious message to analyse.
    language : str
        Language for the explanation: 'english' or 'kannada'. Default: 'english'.

    Returns
    -------
    dict with keys:
        scam_type    (str)   – bank_kyc | courier_customs | fake_official |
                               prize | investment | unknown
        risk         (str)   – low | medium | high
        flagged      (bool)  – True if any red flag found
        signal_count (int)   – number of signals detected
        signals      (list)  – list of signal names found
        verdict      (str)   – plain-language verdict sentence
        instruction  (str)   – one clear action for the reader
        language     (str)   – echoed language used
    """
    result = _classify(message)
    explanation = _explain(result, language)

    return {
        "scam_type": result["scam_type"],
        "risk": result["risk"],
        "flagged": result["flagged"],
        "signal_count": result["signal_count"],
        "signals": [s["name"] for s in result["signals"]],
        "verdict": explanation["verdict"],
        "instruction": explanation["instruction"],
        "language": explanation["language"],
    }


# ---------------------------------------------------------------------------
# Tool 2: send_family_alert
# Simulates alerting a trusted contact on high-risk messages.
# ---------------------------------------------------------------------------

@tool(
    name="send_family_alert",
    description=(
        "Simulate sending an alert to a trusted family contact when a HIGH-RISK "
        "scam message is detected. For medium or low risk, records that no alert "
        "was needed. No real SMS is sent — writes to a local log file."
    ),
    permission=ToolPermission.READ_ONLY,
)
def send_family_alert(
    scam_type: str,
    risk: str,
    contact_name: str = "Family Member",
) -> dict:
    """
    Simulate a family alert for a detected scam result.

    Parameters
    ----------
    scam_type : str
        The scam type returned by analyse_message.
    risk : str
        The risk level returned by analyse_message: low | medium | high.
    contact_name : str
        Name of the trusted contact (use a placeholder — never a real name).

    Returns
    -------
    dict with keys:
        alerted      (bool)  – True if risk was high and alert was sent
        contact_name (str)
        risk         (str)
        message_sent (str)   – the simulated alert text
        timestamp    (str)
    """
    # Reconstruct a minimal result dict that alert_trusted_contact expects
    result = {"risk": risk, "scam_type": scam_type}
    return _alert(result, contact_name)


# ---------------------------------------------------------------------------
# Tool 3: log_scam_case
# Appends a case record for the accuracy report.
# ---------------------------------------------------------------------------

@tool(
    name="log_scam_case",
    description=(
        "Log a scam analysis result to the case database for the accuracy report. "
        "Call this after analyse_message to keep a record. "
        "Uses synthetic message text only — never log real personal data."
    ),
    permission=ToolPermission.READ_ONLY,
)
def log_scam_case(
    message: str,
    scam_type: str,
    risk: str,
    flagged: bool,
    signal_count: int,
) -> dict:
    """
    Append a case record to data/cases.jsonl.

    Parameters
    ----------
    message : str
        The original message text (synthetic only).
    scam_type : str
        Scam type from analyse_message.
    risk : str
        Risk level from analyse_message.
    flagged : bool
        Whether any red flags were found.
    signal_count : int
        Number of signals detected.

    Returns
    -------
    dict with keys:
        logged     (bool)
        case_id    (str)
        timestamp  (str)
        risk       (str)
        scam_type  (str)
        label      (str)
    """
    result = {
        "scam_type": scam_type,
        "risk": risk,
        "flagged": flagged,
        "signal_count": signal_count,
        "signals": [],
        "reasons": [],
    }
    return _log(message, result, label="")
