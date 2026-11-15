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
            # "within N days" is left out: genuine bills and service notices use it constantly
            r"\b(urgent(ly)?|immediately|right now|within \d+ (hours?|minutes?|seconds?)|act now|last chance|expire[sd]?|deadline|limited time|do not delay|today only)\b",
            re.IGNORECASE,
        ),
        "Message uses time-pressure language to rush the recipient.",
    ),
    (
        "arrest_or_seizure_threat",
        re.compile(
            # Bare "police" is left out: genuine notices ("police verification for
            # your passport") mention it, and it fired HIGH + a family alert
            r"\b(arrest(ed)?|digital arrest|warrant|seized?|freeze|frozen|court|cbi|enforcement directorate|cybercrime|legal action|prosecute[d]?|case filed|fir|illegal activit(y|ies)|money laundering)\b",
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
            r"|\b(paypa1|g00gle|amaz0n|yah00|micros0ft|netf1ix)\.(com|net|org|in)\b"
            # OR link shorteners, which hide the real destination
            r"|\b(bit\.ly|tinyurl\.com|goo\.gl|t\.ly|cutt\.ly|is\.gd|rb\.gy|shorturl\.at)/\S+",
            re.IGNORECASE,
        ),
        "Message contains a link that mimics a trusted brand, uses a suspicious domain or hides its destination.",
    ),
    (
        "remote_access_request",
        re.compile(
            r"\b(anydesk|teamviewer|quick ?support|remote(ly)?|screen.?share|install.{0,20}app|download.{0,20}app|click.{0,30}link.{0,20}install)\b",
            re.IGNORECASE,
        ),
        "Message requests remote access to the recipient's device.",
    ),
    (
        # "Digital arrest" scams keep the victim isolated on a call and silent.
        # The lookahead skips bank advice like "do not tell anyone your PIN".
        "secrecy_pressure",
        re.compile(
            r"\b((do not|don't|dont) (tell|inform) (anyone|anybody|your family|family)(?!.{0,20}\b(otp|pin|password|cvv)\b)"
            r"|keep (this|it) (secret|confidential)"
            r"|stay on (the |this )?(video )?call"
            r"|(do not|don't) (disconnect|cut|end) (the|this) call)\b",
            re.IGNORECASE,
        ),
        "Message tells you to keep it secret or stay on a call, a common 'digital arrest' tactic.",
    ),
    (
        "new_number_claim",
        re.compile(
            r"\b(this is my new number|my new number|changed my number|my (old )?phone (broke|is broken|got lost|is lost|is not working))\b",
            re.IGNORECASE,
        ),
        "Message claims to be someone you know writing from a new number.",
    ),
    (
        "money_transfer_request",
        re.compile(
            # A specific amount, OR money directed somewhere specific / for a
            # pretext. Plain "send money to any UPI ID" (a genuine app promo) is not enough.
            r"\b(send|transfer|deposit)\b.{0,30}(\brs\.?\s?\d|₹\s?\d)"
            r"|\b(send|transfer|deposit)\b.{0,15}\b(money|funds|amount)\b.{0,25}"
            r"\b(to (this|my|our|the following)|for verification|immediately|urgently|now)\b"
            # OR a fee demanded to release a parcel, prize or account
            r"|\bpay\b.{0,20}\b(clearance|customs|release|processing|registration|verification) (fee|charges?)\b",
            re.IGNORECASE,
        ),
        "Message asks you to send or transfer money.",
    ),
    (
        "unrealistic_reward",
        re.compile(
            r"\b(you('ve| have)? won|lucky draw|lottery|jackpot"
            r"|guaranteed.{0,25}(returns?|profit)|double your money"
            r"|\d+\s?% (daily|weekly|monthly) (returns?|profit)"
            r"|earn (rs\.?|₹)\s?[\d,]+ (daily|per day|a day)"
            r"|part[- ]time job|like (youtube )?videos)",
            re.IGNORECASE,
        ),
        "Message promises an unrealistic prize, profit or easy income.",
    ),
]


# Genuine bank OTP SMSes say "Do not share this OTP" — that is a warning, not a
# request, so an OTP match directly preceded by a negation must not count.
# Only filler words may sit between the negation and the verb ("never ask you
# to share"); otherwise "Do not ignore this message, enter your PIN" would hide.
_NEGATION_BEFORE = re.compile(
    r"\b(do not|don't|dont|never|not to|must not|should not)\s+"
    r"((ask|asks|asked|request|requests|you|to|ever|will)\s+){0,3}$",
    re.IGNORECASE,
)


def _matches(name: str, pattern: re.Pattern[str], message: str) -> bool:
    """True if *pattern* matches, ignoring negated OTP warnings."""
    if name != "otp_or_pin_request":
        return pattern.search(message) is not None
    # Restart one character after each rejected match: finditer would skip
    # overlapping matches, so "Do not tell anyone. Send the OTP" would be missed.
    pos = 0
    while (m := pattern.search(message, pos)) is not None:
        if not _NEGATION_BEFORE.search(message[: m.start()]):
            return True
        pos = m.start() + 1
    return False


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
        if _matches(name, pattern, message):
            found.append({"name": name, "reason": reason})

    return {
        "flagged": len(found) > 0,
        "signals": found,
        "count": len(found),
    }
