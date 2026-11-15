"""
api.py
Flask REST API — exposes ScamShield pipeline to the React frontend.

Usage:
    python api.py

Endpoints:
    POST /analyse   { "message": "...", "language": "english" }
                    -> full pipeline result
    GET  /health    -> { "status": "ok" }
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Any

from tools.classify_and_score import classify_and_score
from tools.explain_in_language import explain_in_language
from tools.alert_and_log import alert_trusted_contact, log_case

app = Flask(__name__)
CORS(app)  # allow React dev server on different port


@app.get("/health")
def health() -> Any:
    return jsonify({"status": "ok"})


@app.post("/analyse")
def analyse() -> Any:
    data: dict = request.get_json(silent=True) or {}
    message: str = data.get("message", "").strip()
    language: str = data.get("language", "english").strip().lower()

    if not message:
        return jsonify({"error": "message is required"}), 400

    result      = classify_and_score(message)
    explanation = explain_in_language(result, language)
    alert       = alert_trusted_contact(result, contact_name="Family Member")
    logged      = log_case(message, result)

    return jsonify({
        "scam_type":    result["scam_type"],
        "risk":         result["risk"],
        "flagged":      result["flagged"],
        "signal_count": result["signal_count"],
        "signals":      [s["name"] for s in result["signals"]],
        "reasons":      result["reasons"],
        "verdict":      explanation["verdict"],
        "instruction":  explanation["instruction"],
        "language":     explanation["language"],
        "alerted":      alert["alerted"],
        "alert_text":   alert["message_sent"],
        "case_id":      logged["case_id"],
    })


if __name__ == "__main__":
    app.run(debug=False, port=5000)
