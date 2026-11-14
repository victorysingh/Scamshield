"""
evaluate.py
Run the synthetic test set and print detection rate and false-alarm rate.

Usage:
    python evaluate.py

Output (example):
    Test set size : 45
    Scam messages : 30
    Genuine msgs  : 15
    ─────────────────────────
    Detection rate  : 93.3%  (28/30 scams flagged medium or high)
    False-alarm rate:  6.7%  (1/15 genuine flagged)
    ─────────────────────────
    Results written to data/eval_results.json
"""

import json
from pathlib import Path
from typing import Any

from tools.classify_and_score import classify_and_score
from tools.alert_and_log import log_case

_DATA_DIR = Path(__file__).parent / "data"
_TEST_FILE = _DATA_DIR / "test_messages.json"
_RESULTS_FILE = _DATA_DIR / "eval_results.json"


def run_evaluation() -> dict[str, Any]:
    """
    Load test_messages.json, classify every message, compute metrics.

    Returns
    -------
    dict with keys:
        set_size, scam_count, genuine_count,
        detected, false_alarms,
        detection_rate, false_alarm_rate,
        results (list of per-message dicts)
    """
    with _TEST_FILE.open(encoding="utf-8") as fh:
        messages: list[dict[str, Any]] = json.load(fh)

    results: list[dict[str, Any]] = []
    scam_count = 0
    genuine_count = 0
    detected = 0        # scam flagged medium or high
    false_alarms = 0    # genuine flagged medium or high

    for item in messages:
        msg_id: str = item["id"]
        text: str = item["text"]
        true_label: str = item["label"]   # 'scam' or 'genuine'

        result = classify_and_score(text)
        predicted_risk: str = result["risk"]
        flagged = predicted_risk in ("medium", "high")

        # Log to cases.jsonl
        log_case(text, result, label=true_label)

        row: dict[str, Any] = {
            "id": msg_id,
            "label": true_label,
            "scam_type": item.get("type", ""),
            "predicted_risk": predicted_risk,
            "predicted_scam_type": result["scam_type"],
            "flagged": flagged,
            "signals": [s["name"] for s in result["signals"]],
        }
        results.append(row)

        if true_label == "scam":
            scam_count += 1
            if flagged:
                detected += 1
        else:
            genuine_count += 1
            if flagged:
                false_alarms += 1

    set_size = len(messages)
    detection_rate = (detected / scam_count * 100) if scam_count else 0.0
    false_alarm_rate = (false_alarms / genuine_count * 100) if genuine_count else 0.0

    summary: dict[str, Any] = {
        "set_size": set_size,
        "scam_count": scam_count,
        "genuine_count": genuine_count,
        "detected": detected,
        "false_alarms": false_alarms,
        "detection_rate": round(detection_rate, 1),
        "false_alarm_rate": round(false_alarm_rate, 1),
        "note": "Synthetic test set only. Do not claim production accuracy.",
        "results": results,
    }

    _RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _RESULTS_FILE.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)

    return summary


def _print_report(s: dict[str, Any]) -> None:
    sep = "-" * 40
    print(f"\n{'ScamShield - Evaluation Report':^40}")
    print(sep)
    print(f"  Test set size    : {s['set_size']}")
    print(f"  Scam messages    : {s['scam_count']}")
    print(f"  Genuine messages : {s['genuine_count']}")
    print(sep)
    print(f"  Detection rate   : {s['detection_rate']:.1f}%  "
          f"({s['detected']}/{s['scam_count']} scams flagged medium/high)")
    print(f"  False-alarm rate : {s['false_alarm_rate']:.1f}%  "
          f"({s['false_alarms']}/{s['genuine_count']} genuine flagged)")
    print(sep)
    print(f"  Results written  -> {_RESULTS_FILE}")
    print(f"  WARNING: Synthetic set only - do not claim production accuracy.\n")


if __name__ == "__main__":
    summary = run_evaluation()
    _print_report(summary)
