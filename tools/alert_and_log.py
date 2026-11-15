"""
alert_and_log.py
Two tools:
  alert_trusted_contact(result, contact_name) — simulated alert, writes to file
  log_case(message, result)                   — appends a case record to JSONL log

Both return plain JSON. No real SMS or network call is made.
"""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Monotonic counter ensures case IDs are unique even within the same microsecond
_counter_lock = threading.Lock()
_case_counter: int = 0


def _next_counter() -> int:
    global _case_counter
    with _counter_lock:
        _case_counter += 1
        return _case_counter

# ---------------------------------------------------------------------------
# File paths  (relative to project root; created if absent)
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).parent.parent / "data"
_ALERT_FILE = _DATA_DIR / "alerts.jsonl"
_LOG_FILE = _DATA_DIR / "cases.jsonl"


def _append_line(path: Path, line: str) -> bool:
    """
    Append one JSON line; return False instead of raising if the disk is not
    writable. Hosted runtimes such as watsonx Orchestrate may mount the tool
    package read-only, and a failed log must never break the scam verdict.
    """
    try:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return True
    except OSError:
        return False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Tool 1: alert_trusted_contact
# ---------------------------------------------------------------------------

def alert_trusted_contact(
    result: dict[str, Any],
    contact_name: str = "Family Member",
) -> dict[str, Any]:
    """
    Simulate sending an alert to a trusted contact when risk is high.

    For non-high risk, records a note that no alert was needed.
    No real SMS or network call is made — writes to data/alerts.jsonl.

    Parameters
    ----------
    result : dict
        Output of classify_and_score().
    contact_name : str
        Name of the trusted contact (synthetic placeholder only).

    Returns
    -------
    dict with keys:
        alerted      (bool)
        contact_name (str)
        risk         (str)
        message_sent (str)  – the simulated alert text
        timestamp    (str)
        written      (bool) – False if the alert file could not be written
    """
    risk: str = result.get("risk", "low")
    scam_type: str = result.get("scam_type", "unknown")
    alerted = risk == "high"

    if alerted:
        message_sent = (
            f"[SIMULATED ALERT to {contact_name}] "
            f"A HIGH-RISK {scam_type.replace('_', ' ')} message was detected "
            f"on the protected device. Please check on them immediately. "
            f"ScamShield ref: {_now_iso()}"
        )
    else:
        message_sent = f"[NO ALERT] Risk is '{risk}' — no alert needed."

    record: dict[str, Any] = {
        "timestamp": _now_iso(),
        "alerted": alerted,
        "contact_name": contact_name,
        "risk": risk,
        "scam_type": scam_type,
        "message_sent": message_sent,
    }

    record["written"] = _append_line(_ALERT_FILE, json.dumps(record))
    return record


# ---------------------------------------------------------------------------
# Tool 2: log_case
# ---------------------------------------------------------------------------

def log_case(
    message: str,
    result: dict[str, Any],
    label: str = "",
) -> dict[str, Any]:
    """
    Append a case record to data/cases.jsonl for the accuracy report.

    Parameters
    ----------
    message : str
        The original message text (synthetic only — never real personal data).
    result : dict
        Output of classify_and_score().
    label : str
        Ground-truth label for evaluation: 'scam' | 'genuine' | '' (unknown).

    Returns
    -------
    dict with keys:
        logged     (bool) – False if the log file could not be written
        case_id    (str)
        timestamp  (str)
        risk       (str)
        scam_type  (str)
        label      (str)
    """
    case_id = f"CASE-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}-{_next_counter():04d}"
    timestamp = _now_iso()

    record: dict[str, Any] = {
        "case_id": case_id,
        "timestamp": timestamp,
        "message": message,
        "scam_type": result.get("scam_type", "unknown"),
        "risk": result.get("risk", "low"),
        "flagged": result.get("flagged", False),
        "signal_count": result.get("signal_count", 0),
        "label": label,
    }

    logged = _append_line(_LOG_FILE, json.dumps(record, ensure_ascii=False))

    return {
        "logged": logged,
        "case_id": case_id,
        "timestamp": timestamp,
        "risk": record["risk"],
        "scam_type": record["scam_type"],
        "label": label,
    }
