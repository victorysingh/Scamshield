"""
check_red_flags.py
Detects named red-flag signals in a text message.
Returns plain JSON (dict) — safe to pass straight to the Orchestrate agent.
"""

import re
from typing import Any

# ---------------------------------------------------------------------------
# Signal definitions
# Each entry: (signal_name, compiled_pattern, short_reason)
# ---------------------------------------------------------------------------

_SIGNALS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "otp_or_pin_request",
        re.compile(
            r"\b(share|send|give|provide|enter|tell)\b.{0,40}\b(otp|one[- ]time[- ]password|pin|password|passcode)\b",
            re.IGNORECASE,
        ),
        "Message asks the recipient to share an OTP, PIN or password.",
    ),
    (
        "urgency_language",
        re.compile(
            r"\b(urgent|immediately|right now|within \d+ (hours?|minutes?|seconds?|days?)|act now|last chance|expire[sd]?|deadline|limited time|do not delay|today only)\b",
            re.IGNORECASE,
        ),
        "Message uses time-pressure language to rush the recipient.",
    ),
    (
        "arrest_or_seizure_threat",
        re.compile(
            r"\b(arrest(ed)?|warrant|seized?|freeze|frozen|court|police|cbi|enforcement directorate|cybercrime|legal action|prosecute[d]?|case filed|fir)\b",
            re.IGNORECASE,
        ),
        "Message threatens arrest, legal action or asset seizure.",
    ),
    (
        "lookalike_link",
        re.compile(
            # Match URLs with suspicious TLDs
            r"https?://[^\s]*[-_.][^\s]*\.(xyz|top|click|link|tk|ml|ga|cf|gq|pw|cc|icu)"
            # OR URLs containing lookalike brand names
            r"|https?://[^\s]*(paypa1|g00gle|amaz0n|yah00|micros0ft|netf1ix|sbi[-_]?secure|hdfc[-_]?verify|axis[-_]?update)[^\s]*"
            # OR plain-text (no http) lookalike brand domains anywhere in message
            r"|\b(paypa1|g00gle|amaz0n|yah00|micros0ft|netf1ix)\.(com|net|org|in)\b",
            re.IGNORECASE,
        ),
        "Message contains a link that mimics a trusted brand or uses a suspicious domain.",
    ),
    (
        "remote_access_request",
        re.compile(
            r"\b(anydesk|teamviewer|quick ?support|remote(ly)?|screen.?share|install.{0,20}app|download.{0,20}app|click.{0,30}link.{0,20}install)\b",
            re.IGNORECASE,
        ),
        "Message requests remote access to the recipient's device.",
    ),
]


def check_red_flags(message: str) -> dict[str, Any]:
    """
    Scan *message* for known scam red-flag signals.

    Parameters
    ----------
    message : str
        The raw text of the message to analyse.

    Returns
    -------
    dict with keys:
        flagged  (bool)  – True if at least one signal was found.
        signals  (list)  – Zero or more dicts, each with:
                              name   (str) signal identifier
                              reason (str) one-sentence explanation
        count    (int)   – Number of signals detected.
    """
    if not isinstance(message, str):
        return {"flagged": False, "signals": [], "count": 0}

    found: list[dict[str, str]] = []
    for name, pattern, reason in _SIGNALS:
        if pattern.search(message):
            found.append({"name": name, "reason": reason})

    return {
        "flagged": len(found) > 0,
        "signals": found,
        "count": len(found),
    }
