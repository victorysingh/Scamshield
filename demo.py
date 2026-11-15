"""
demo.py
ScamShield interactive demo — runs the full pipeline locally without Orchestrate.
# -*- coding: utf-8 -*-

Usage:
    python demo.py                        # interactive mode — paste any message
    python demo.py --message "your text"  # single message mode
    python demo.py --language kannada     # Kannada output
    python demo.py --run-samples          # run 3 built-in demo messages

Output shows:
    - Risk level, scam type, signals detected
    - Plain-language verdict + instruction (English or Kannada)
    - Simulated family alert (high-risk only)
    - Case ID logged to data/cases.jsonl
"""

import argparse
import io
import json
import sys
from typing import Any

# Force UTF-8 output on Windows terminals (handles Kannada + emoji)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from tools.classify_and_score import classify_and_score
from tools.explain_in_language import explain_in_language
from tools.alert_and_log import alert_trusted_contact, log_case

# ---------------------------------------------------------------------------
# Risk colour/badge (ASCII safe for all terminals)
# ---------------------------------------------------------------------------

_RISK_BADGE: dict[str, str] = {
    "high":   "[ HIGH RISK ]",
    "medium": "[ MEDIUM RISK ]",
    "low":    "[ LOW RISK ]",
}

_SCAM_LABEL: dict[str, str] = {
    "bank_kyc":        "Bank / KYC Scam",
    "courier_customs": "Courier / Customs Scam",
    "fake_official":   "Fake Government Official Scam",
    "prize":           "Fake Prize / Lottery Scam",
    "investment":      "Fake Investment Scam",
    "unknown":         "Suspicious Message (type unknown)",
}

# ---------------------------------------------------------------------------
# Built-in sample messages for the demo
# ---------------------------------------------------------------------------

SAMPLES: list[dict[str, str]] = [
    {
        "label": "SCAM — Fake Official (High Risk)",
        "text": (
            "CBI cybercrime department: A case filed against your mobile number "
            "for money laundering. Cooperate or face arrest. "
            "Install AnyDesk and share the ID with our officer immediately."
        ),
    },
    {
        "label": "SCAM — Bank/KYC (Medium Risk)",
        "text": (
            "Dear customer, your SynthBank account KYC is incomplete. "
            "Share your OTP immediately to avoid suspension. Call 99900-00001."
        ),
    },
    {
        "label": "GENUINE — Bank Transaction",
        "text": (
            "SynthBank: Rs.1,500 debited from account XX0042 at SynthMart "
            "on 14-Nov-2026. Balance: Rs.12,340. "
            "If not done by you, call 1800-000-0000."
        ),
    },
]

# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

def run_pipeline(message: str, language: str = "english") -> dict[str, Any]:
    """Run classify -> explain -> alert -> log and return combined result."""
    result     = classify_and_score(message)
    explanation = explain_in_language(result, language)
    alert      = alert_trusted_contact(result, contact_name="Family Member")
    logged     = log_case(message, result)
    return {
        "result":      result,
        "explanation": explanation,
        "alert":       alert,
        "logged":      logged,
    }


def print_report(message: str, data: dict[str, Any]) -> None:
    """Pretty-print the pipeline output to stdout."""
    r   = data["result"]
    exp = data["explanation"]
    alr = data["alert"]
    lg  = data["logged"]

    sep = "-" * 60
    print(f"\n{sep}")
    print(f"  ScamShield Analysis Report")
    print(sep)
    print(f"  Message  : {message[:80]}{'...' if len(message) > 80 else ''}")
    print(sep)
    print(f"  {_RISK_BADGE.get(r['risk'], r['risk'].upper())}")
    print(f"  Scam Type: {_SCAM_LABEL.get(r['scam_type'], r['scam_type'])}")
    print(f"  Signals  : {r['signal_count']} detected")
    for sig in r["signals"]:
        print(f"             - {sig['name']}: {sig['reason']}")
    print(sep)
    print(f"  Verdict  : {exp['verdict']}")
    print(f"  Action   : {exp['instruction']}")
    print(f"  Language : {exp['language'].capitalize()}")
    print(sep)
    if alr["alerted"]:
        print(f"  ** ALERT SENT to {alr['contact_name']} (simulated) **")
        print(f"     {alr['message_sent']}")
    else:
        print(f"  No family alert needed (risk is {r['risk']}).")
    print(sep)
    print(f"  Case logged: {lg['case_id']}")
    print(f"\n  If you are unsure, call the National Cyber Crime Helpline: 1930")
    print(f"{sep}\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ScamShield — Scam message analyser demo"
    )
    parser.add_argument("--message",     type=str, help="Message text to analyse")
    parser.add_argument("--language",    type=str, default="english",
                        choices=["english", "kannada"],
                        help="Output language (default: english)")
    parser.add_argument("--run-samples", action="store_true",
                        help="Run the 3 built-in demo messages")
    parser.add_argument("--json",        action="store_true",
                        help="Output raw JSON instead of formatted report")
    args = parser.parse_args()

    if args.run_samples:
        for sample in SAMPLES:
            print(f"\n>>> Sample: {sample['label']}")
            data = run_pipeline(sample["text"], args.language)
            if args.json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                print_report(sample["text"], data)
        return

    if args.message:
        message = args.message
    else:
        # Interactive mode
        print("\nScamShield Interactive Demo")
        print("Paste a suspicious message and press Enter twice (blank line to submit).")
        print("Type 'quit' to exit.\n")
        lines: list[str] = []
        while True:
            try:
                line = input()
            except (EOFError, KeyboardInterrupt):
                break
            if line.strip().lower() == "quit":
                sys.exit(0)
            if line == "" and lines:
                break
            lines.append(line)
        message = " ".join(lines).strip()
        if not message:
            print("No message entered.")
            sys.exit(0)

    data = run_pipeline(message, args.language)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_report(message, data)


if __name__ == "__main__":
    main()
