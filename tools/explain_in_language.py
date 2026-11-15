"""
explain_in_language.py
Produces a plain-language explanation of a classify_and_score result
in English or Kannada (ಕನ್ನಡ).

Rules:
- One clear verdict sentence
- One plain instruction (what the person should do)
- No jargon
- Returns plain JSON
"""

from typing import Any

# ---------------------------------------------------------------------------
# English templates
# ---------------------------------------------------------------------------

_EN_VERDICT: dict[str, str] = {
    "high":   "⚠️ This message is very likely a scam. Do not respond or share any information.",
    "medium": "⚠️ This message has suspicious signs. Be careful before taking any action.",
    "low":    "✅ This message looks genuine, but always stay alert.",
}

_EN_INSTRUCTION: dict[str, str] = {
    "bank_kyc":        "Never share your OTP, PIN, password or Aadhaar number with anyone over the phone or message.",
    "courier_customs": "Do not pay any fee through a link in a message. Contact the courier company directly using their official website.",
    "fake_official":   "Real government agencies never ask for money or personal details over phone or SMS. Hang up and call the official helpline.",
    "prize":           "You cannot win a prize you never entered. Ignore this message and block the sender.",
    "investment":      "No legitimate investment guarantees high returns. Do not send money. Talk to a trusted family member first.",
    "unknown":         "If you are unsure, show this message to a family member or call the National Cyber Crime helpline: 1930.",
}

# ---------------------------------------------------------------------------
# Kannada templates
# ---------------------------------------------------------------------------

_KN_VERDICT: dict[str, str] = {
    "high":   "⚠️ ಈ ಸಂದೇಶವು ಬಹುಶಃ ಮೋಸದ ಸಂದೇಶ. ಯಾವುದೇ ಮಾಹಿತಿಯನ್ನು ಹಂಚಿಕೊಳ್ಳಬೇಡಿ ಅಥವಾ ಪ್ರತಿಕ್ರಿಯಿಸಬೇಡಿ.",
    "medium": "⚠️ ಈ ಸಂದೇಶದಲ್ಲಿ ಅನುಮಾನಾಸ್ಪದ ಸಂಗತಿಗಳಿವೆ. ಯಾವುದೇ ಕ್ರಮ ತೆಗೆದುಕೊಳ್ಳುವ ಮೊದಲು ಎಚ್ಚರಿಕೆಯಿಂದ ಇರಿ.",
    "low":    "✅ ಈ ಸಂದೇಶವು ನಿಜವಾದದ್ದಾಗಿ ಕಾಣುತ್ತದೆ, ಆದರೆ ಯಾವಾಗಲೂ ಎಚ್ಚರದಿಂದ ಇರಿ.",
}

_KN_INSTRUCTION: dict[str, str] = {
    "bank_kyc":        "ಫೋನ್ ಅಥವಾ ಸಂದೇಶದ ಮೂಲಕ ಯಾರಿಗೂ ನಿಮ್ಮ OTP, PIN, ಪಾಸ್‌ವರ್ಡ್ ಅಥವಾ ಆಧಾರ್ ಸಂಖ್ಯೆ ನೀಡಬೇಡಿ.",
    "courier_customs": "ಸಂದೇಶದಲ್ಲಿರುವ ಲಿಂಕ್ ಮೂಲಕ ಹಣ ಪಾವತಿಸಬೇಡಿ. ಅಧಿಕೃತ ವೆಬ್‌ಸೈಟ್ ಮೂಲಕ ಕೊರಿಯರ್ ಕಂಪನಿಯನ್ನು ನೇರವಾಗಿ ಸಂಪರ್ಕಿಸಿ.",
    "fake_official":   "ನಿಜವಾದ ಸರ್ಕಾರಿ ಸಂಸ್ಥೆಗಳು ಎಂದಿಗೂ ಫೋನ್ ಅಥವಾ SMS ಮೂಲಕ ಹಣ ಅಥವಾ ವೈಯಕ್ತಿಕ ವಿವರ ಕೇಳುವುದಿಲ್ಲ. ಫೋನ್ ಕಟ್ ಮಾಡಿ ಮತ್ತು ಅಧಿಕೃತ ಹೆಲ್ಪ್‌ಲೈನ್‌ಗೆ ಕರೆ ಮಾಡಿ.",
    "prize":           "ನೀವು ಭಾಗವಹಿಸದ ಸ್ಪರ್ಧೆಯಲ್ಲಿ ಬಹುಮಾನ ಗೆಲ್ಲಲು ಸಾಧ್ಯವಿಲ್ಲ. ಈ ಸಂದೇಶವನ್ನು ನಿರ್ಲಕ್ಷಿಸಿ ಮತ್ತು ಕಳುಹಿಸಿದವರನ್ನು ಬ್ಲಾಕ್ ಮಾಡಿ.",
    "investment":      "ಯಾವುದೇ ಹೂಡಿಕೆ ಹೆಚ್ಚಿನ ಲಾಭ ಖಾತರಿ ನೀಡುವುದಿಲ್ಲ. ಹಣ ಕಳುಹಿಸಬೇಡಿ. ಮೊದಲು ವಿಶ್ವಾಸಾರ್ಹ ಕುಟುಂಬ ಸದಸ್ಯರೊಂದಿಗೆ ಮಾತನಾಡಿ.",
    "unknown":         "ನಿಮಗೆ ಅನುಮಾನವಿದ್ದರೆ, ಈ ಸಂದೇಶವನ್ನು ಕುಟುಂಬ ಸದಸ್ಯರಿಗೆ ತೋರಿಸಿ ಅಥವಾ ರಾಷ್ಟ್ರೀಯ ಸೈಬರ್ ಕ್ರೈಮ್ ಹೆಲ್ಪ್‌ಲೈನ್‌ಗೆ ಕರೆ ಮಾಡಿ: 1930.",
}

_SUPPORTED_LANGUAGES = {"english", "kannada"}


def explain_in_language(result: dict[str, Any], language: str) -> dict[str, Any]:
    """
    Generate a plain-language explanation from a classify_and_score result.

    Parameters
    ----------
    result : dict
        Output of classify_and_score().
    language : str
        'english' or 'kannada' (case-insensitive).

    Returns
    -------
    dict with keys:
        language    (str)
        verdict     (str) – one sentence verdict
        instruction (str) – one clear action for the reader
        risk        (str) – echoed from result
        scam_type   (str) – echoed from result
    """
    if not isinstance(result, dict):
        return {
            "language": language,
            "verdict": "Unable to explain: invalid result.",
            "instruction": "",
            "risk": "unknown",
            "scam_type": "unknown",
        }

    lang = language.strip().lower() if isinstance(language, str) else "english"
    if lang not in _SUPPORTED_LANGUAGES:
        lang = "english"

    risk: str = result.get("risk", "low")
    scam_type: str = result.get("scam_type", "unknown")

    if lang == "kannada":
        verdict = _KN_VERDICT.get(risk, _KN_VERDICT["low"])
        instruction = _KN_INSTRUCTION.get(scam_type, _KN_INSTRUCTION["unknown"])
    else:
        verdict = _EN_VERDICT.get(risk, _EN_VERDICT["low"])
        instruction = _EN_INSTRUCTION.get(scam_type, _EN_INSTRUCTION["unknown"])

    return {
        "language": lang,
        "verdict": verdict,
        "instruction": instruction,
        "risk": risk,
        "scam_type": scam_type,
    }
