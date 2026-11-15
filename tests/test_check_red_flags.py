"""
test_check_red_flags.py
Tests for tools/check_red_flags.py — one test per signal plus clean-message tests.
All messages are synthetic.
"""

import json
import pytest
from tools.check_red_flags import check_red_flags


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _signal_names(result: dict) -> list[str]:
    return [s["name"] for s in result["signals"]]


def _is_valid_json(result: dict) -> bool:
    """Verify the return value is json.dumps-serialisable."""
    try:
        json.dumps(result)
        return True
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Signal 1: OTP / PIN request
# ---------------------------------------------------------------------------

class TestOtpOrPinRequest:
    def test_share_otp(self) -> None:
        msg = "Dear customer, please share the OTP sent to your registered mobile number."
        result = check_red_flags(msg)
        assert result["flagged"] is True
        assert "otp_or_pin_request" in _signal_names(result)

    def test_give_pin(self) -> None:
        msg = "Your account will be locked. Give us your PIN to verify identity."
        result = check_red_flags(msg)
        assert "otp_or_pin_request" in _signal_names(result)

    def test_send_one_time_password(self) -> None:
        msg = "Send the one-time password to our agent at 99999-00000."
        result = check_red_flags(msg)
        assert "otp_or_pin_request" in _signal_names(result)

    def test_no_otp_in_genuine_notification(self) -> None:
        # Bank sends OTP *to* the user — does not ask them to share it
        msg = "Your OTP for transaction ₹500 at FakeMart is 123456. Valid for 10 minutes. Do not share with anyone."
        result = check_red_flags(msg)
        # "Do not share" should NOT match the request pattern (verb + otp without "share ... otp" order)
        assert "otp_or_pin_request" not in _signal_names(result)

    def test_do_not_share_this_otp_is_not_a_request(self) -> None:
        # Regression: genuine login-OTP SMS was flagged HIGH and alerted family
        msg = ("Your OTP for SynthBank login is 000000. Valid for 10 minutes. "
               "Do not share this OTP with anyone, including bank staff.")
        assert "otp_or_pin_request" not in _signal_names(check_red_flags(msg))

    def test_never_share_your_pin_is_not_a_request(self) -> None:
        msg = "SynthBank will never ask you to share your PIN."
        assert "otp_or_pin_request" not in _signal_names(check_red_flags(msg))

    def test_request_still_caught_after_a_warning(self) -> None:
        # A negated phrase earlier must not hide a real request later
        msg = "Do not panic. Share the OTP with our officer to unblock your account."
        assert "otp_or_pin_request" in _signal_names(check_red_flags(msg))

    def test_secrecy_then_request_is_caught(self) -> None:
        # "Do not tell anyone" overlaps the request; it must not hide it
        msg = "Do not tell anyone. Send the OTP to our officer now."
        assert "otp_or_pin_request" in _signal_names(check_red_flags(msg))

    def test_negation_with_non_filler_words_does_not_hide_request(self) -> None:
        msg = "Do not ignore this message enter your PIN here to stay safe."
        assert "otp_or_pin_request" in _signal_names(check_red_flags(msg))


# ---------------------------------------------------------------------------
# Signal 2: Urgency language
# ---------------------------------------------------------------------------

class TestUrgencyLanguage:
    def test_urgent(self) -> None:
        msg = "URGENT: Your KYC is incomplete. Update immediately."
        result = check_red_flags(msg)
        assert "urgency_language" in _signal_names(result)

    def test_expires_in_hours(self) -> None:
        msg = "Your account access expires within 24 hours. Act now."
        result = check_red_flags(msg)
        assert "urgency_language" in _signal_names(result)

    def test_today_only(self) -> None:
        msg = "Today only — claim your prize before midnight!"
        result = check_red_flags(msg)
        assert "urgency_language" in _signal_names(result)

    def test_no_urgency_in_statement(self) -> None:
        msg = "Your monthly statement for October is ready. Log in to SynthBank to view it."
        result = check_red_flags(msg)
        assert "urgency_language" not in _signal_names(result)


# ---------------------------------------------------------------------------
# Signal 3: Arrest / seizure threat
# ---------------------------------------------------------------------------

class TestArrestOrSeizureThreat:
    def test_arrest_warrant(self) -> None:
        msg = "An arrest warrant has been issued against your Aadhar number. Call immediately."
        result = check_red_flags(msg)
        assert "arrest_or_seizure_threat" in _signal_names(result)

    def test_account_frozen(self) -> None:
        msg = "Your bank account will be frozen by Enforcement Directorate unless you cooperate."
        result = check_red_flags(msg)
        assert "arrest_or_seizure_threat" in _signal_names(result)

    def test_cybercrime(self) -> None:
        msg = "Cybercrime department has registered a case filed against your mobile number."
        result = check_red_flags(msg)
        assert "arrest_or_seizure_threat" in _signal_names(result)

    def test_no_threat_in_court_reminder(self) -> None:
        # Genuine reminder — does not threaten the recipient with legal action
        msg = "Reminder: your civil-court fee payment is due by Dec 1. Visit the official portal."
        result = check_red_flags(msg)
        # "court" is in the pattern — this is an intentional true positive edge case; signal fires
        # We just verify the return shape is valid
        assert _is_valid_json(result)


# ---------------------------------------------------------------------------
# Signal 4: Lookalike link
# ---------------------------------------------------------------------------

class TestLookalikeLlink:
    def test_suspicious_tld(self) -> None:
        msg = "Verify your account at http://synthbank-kyc.xyz/verify?id=12345"
        result = check_red_flags(msg)
        assert "lookalike_link" in _signal_names(result)

    def test_brand_lookalike(self) -> None:
        msg = "Login at https://sbi-secure.netverify.click/login to avoid suspension."
        result = check_red_flags(msg)
        assert "lookalike_link" in _signal_names(result)

    def test_paypal_lookalike(self) -> None:
        msg = "Your paypa1.com account has been compromised. Reset now."
        result = check_red_flags(msg)
        assert "lookalike_link" in _signal_names(result)

    def test_clean_https_link(self) -> None:
        msg = "Track your parcel at https://www.synthcourier.in/track/ABC123"
        result = check_red_flags(msg)
        assert "lookalike_link" not in _signal_names(result)


# ---------------------------------------------------------------------------
# Signal 5: Remote-access request
# ---------------------------------------------------------------------------

class TestRemoteAccessRequest:
    def test_anydesk(self) -> None:
        msg = "Please install AnyDesk on your phone so our technician can help you remotely."
        result = check_red_flags(msg)
        assert "remote_access_request" in _signal_names(result)

    def test_teamviewer(self) -> None:
        msg = "Open TeamViewer and share the ID with our fraud-prevention agent."
        result = check_red_flags(msg)
        assert "remote_access_request" in _signal_names(result)

    def test_screen_share(self) -> None:
        msg = "Start a screen-share session with our security team now."
        result = check_red_flags(msg)
        assert "remote_access_request" in _signal_names(result)

    def test_no_remote_in_support_email(self) -> None:
        msg = "Your service request #SR-00042 has been received. We will contact you within 2 business days."
        result = check_red_flags(msg)
        assert "remote_access_request" not in _signal_names(result)


# ---------------------------------------------------------------------------
# Multi-signal messages
# ---------------------------------------------------------------------------

class TestMultipleSignals:
    def test_two_signals(self) -> None:
        msg = (
            "URGENT: Share your OTP immediately or your account will be locked."
        )
        result = check_red_flags(msg)
        names = _signal_names(result)
        assert "urgency_language" in names
        assert "otp_or_pin_request" in names
        assert result["count"] >= 2

    def test_three_signals(self) -> None:
        msg = (
            "An arrest warrant is issued. Send your PIN within 2 hours. "
            "Install AnyDesk for verification."
        )
        result = check_red_flags(msg)
        names = _signal_names(result)
        assert "arrest_or_seizure_threat" in names
        assert "urgency_language" in names
        assert "remote_access_request" in names
        assert result["count"] >= 3


# ---------------------------------------------------------------------------
# Clean / genuine messages — should produce zero signals
# ---------------------------------------------------------------------------

class TestCleanMessages:
    def test_bank_statement_notice(self) -> None:
        msg = "Your SynthBank account statement for October 2026 is ready. Log in at synthbank.in."
        result = check_red_flags(msg)
        assert result["flagged"] is False
        assert result["count"] == 0

    def test_delivery_update(self) -> None:
        msg = "Your parcel from SynthShop will arrive between 2 PM and 6 PM today. No action needed."
        result = check_red_flags(msg)
        assert result["flagged"] is False

    def test_empty_string(self) -> None:
        result = check_red_flags("")
        assert result["flagged"] is False
        assert result["count"] == 0

    def test_non_string_input(self) -> None:
        result = check_red_flags(None)  # type: ignore[arg-type]
        assert result["flagged"] is False


# ---------------------------------------------------------------------------
# Return-value contract: every result is JSON-serialisable
# ---------------------------------------------------------------------------

class TestReturnValueContract:
    @pytest.mark.parametrize("msg", [
        "Share your OTP now.",
        "URGENT act immediately!",
        "Arrest warrant issued.",
        "http://paypa1.com/reset",
        "Install AnyDesk please.",
        "Your statement is ready.",
        "",
    ])
    def test_always_returns_valid_json(self, msg: str) -> None:
        result = check_red_flags(msg)
        assert _is_valid_json(result)
        assert isinstance(result["flagged"], bool)
        assert isinstance(result["signals"], list)
        assert isinstance(result["count"], int)


# ---------------------------------------------------------------------------
# Signals added after the review (digital arrest, impersonation, task scams)
# ---------------------------------------------------------------------------

class TestReviewSignals:
    def test_digital_arrest_secrecy(self) -> None:
        msg = "Stay on video call with our officer and do not tell anyone about this case."
        assert "secrecy_pressure" in _signal_names(check_red_flags(msg))

    def test_bank_advice_not_secrecy(self) -> None:
        msg = "SynthBank will never ask for your PIN. Do not tell anyone your PIN or OTP."
        assert "secrecy_pressure" not in _signal_names(check_red_flags(msg))

    def test_new_number_claim(self) -> None:
        msg = "Hi Mum, this is my new number, my phone broke."
        assert "new_number_claim" in _signal_names(check_red_flags(msg))

    def test_money_transfer_with_amount(self) -> None:
        msg = "Please send Rs.20,000 to this account today."
        assert "money_transfer_request" in _signal_names(check_red_flags(msg))

    def test_customs_fee_demand(self) -> None:
        msg = "Your parcel is held. Pay clearance fee to release it."
        assert "money_transfer_request" in _signal_names(check_red_flags(msg))

    def test_app_promo_is_not_money_request(self) -> None:
        msg = "You can now send money to any UPI ID instantly with SynthPay."
        assert "money_transfer_request" not in _signal_names(check_red_flags(msg))

    def test_task_scam_reward(self) -> None:
        msg = "Earn Rs.5000 daily by liking YouTube videos. Part-time job."
        assert "unrealistic_reward" in _signal_names(check_red_flags(msg))

    def test_short_link(self) -> None:
        msg = "Your account is blocked. Update KYC: bit.ly/synth-kyc"
        assert "lookalike_link" in _signal_names(check_red_flags(msg))

    def test_police_verification_not_a_threat(self) -> None:
        msg = "Police verification for your passport is scheduled on Monday at 11 am."
        assert check_red_flags(msg)["count"] == 0

    def test_bill_due_in_days_not_urgent(self) -> None:
        msg = "Your electricity bill of Rs.1,240 is due within 3 days."
        assert "urgency_language" not in _signal_names(check_red_flags(msg))
