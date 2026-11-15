import { useState } from "react";
import "./App.css";

const API = "http://localhost:5000";

const RISK_CONFIG = {
  high:   { label: "HIGH RISK",   color: "#c0392b", bg: "#fdecea", icon: "⚠️" },
  medium: { label: "MEDIUM RISK", color: "#e67e22", bg: "#fef3e2", icon: "⚠️" },
  low:    { label: "LOW RISK",    color: "#27ae60", bg: "#eafaf1", icon: "✅" },
};

const SCAM_LABELS = {
  bank_kyc:        "Bank / KYC Scam",
  courier_customs: "Courier / Customs Scam",
  fake_official:   "Fake Government Official Scam",
  prize:           "Fake Prize / Lottery Scam",
  investment:      "Fake Investment Scam",
  unknown:         "No specific scam pattern detected",
};

const SAMPLES = [
  {
    label: "Fake Official (High Risk)",
    text: "CBI cybercrime department: A case filed against your mobile number for money laundering. Cooperate or face arrest. Install AnyDesk and share the ID with our officer immediately.",
  },
  {
    label: "Bank KYC Scam (High Risk)",
    text: "Dear customer, your SynthBank account KYC is incomplete. Share your OTP immediately to avoid suspension. Call 99900-00001.",
  },
  {
    label: "Genuine Bank SMS (Low Risk)",
    text: "SynthBank: Rs.1,500 debited from account XX0042 at SynthMart on 14-Nov-2026. Balance: Rs.12,340. If not done by you, call 1800-000-0000.",
  },
];

export default function App() {
  const [message, setMessage]   = useState("");
  const [language, setLanguage] = useState("english");
  const [result, setResult]     = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  async function analyse() {
    if (!message.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(`${API}/analyse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, language }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch {
      setError("Could not connect to ScamShield API. Make sure api.py is running.");
    } finally {
      setLoading(false);
    }
  }

  function loadSample(text) {
    setMessage(text);
    setResult(null);
    setError("");
  }

  const risk = result ? RISK_CONFIG[result.risk] ?? RISK_CONFIG.low : null;

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-inner">
          <span className="logo">🛡️ ScamShield</span>
          <span className="tagline">AI-powered scam protection for senior citizens</span>
        </div>
      </header>

      <main className="main">
        {/* Input section */}
        <section className="card input-card">
          <h2 className="section-title">Paste a suspicious message</h2>

          {/* Sample buttons */}
          <div className="samples">
            <span className="samples-label">Try a sample:</span>
            {SAMPLES.map((s) => (
              <button key={s.label} className="sample-btn" onClick={() => loadSample(s.text)}>
                {s.label}
              </button>
            ))}
          </div>

          <textarea
            className="textarea"
            rows={5}
            placeholder="Paste the message here..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />

          {/* Language toggle */}
          <div className="lang-row">
            <span className="lang-label">Output language:</span>
            <label className="lang-option">
              <input type="radio" value="english" checked={language === "english"}
                onChange={() => setLanguage("english")} /> English
            </label>
            <label className="lang-option">
              <input type="radio" value="kannada" checked={language === "kannada"}
                onChange={() => setLanguage("kannada")} /> ಕನ್ನಡ (Kannada)
            </label>
          </div>

          <button
            className="analyse-btn"
            onClick={analyse}
            disabled={loading || !message.trim()}
          >
            {loading ? "Analysing…" : "Analyse Message"}
          </button>

          {error && <p className="error-msg">{error}</p>}
        </section>

        {/* Result section */}
        {result && (
          <section className="card result-card" style={{ borderTop: `6px solid ${risk.color}` }}>

            {/* Risk badge */}
            <div className="risk-badge" style={{ background: risk.bg, color: risk.color }}>
              <span className="risk-icon">{risk.icon}</span>
              <span className="risk-label">{risk.label}</span>
            </div>

            {/* Scam type */}
            <p className="scam-type">
              <strong>Type:</strong> {SCAM_LABELS[result.scam_type] ?? result.scam_type}
            </p>

            {/* Verdict */}
            <div className="verdict-box">
              <p className="verdict">{result.verdict}</p>
              <p className="instruction">{result.instruction}</p>
            </div>

            {/* Signals */}
            {result.signal_count > 0 && (
              <div className="signals">
                <p className="signals-title">⚡ Warning signals detected ({result.signal_count}):</p>
                <ul className="signals-list">
                  {result.signals.map((s) => (
                    <li key={s}>{s.replace(/_/g, " ")}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Family alert */}
            <div className={`alert-box ${result.alerted ? "alert-sent" : "alert-none"}`}>
              {result.alerted
                ? "📲 Family alert logged (simulated)"
                : "No family alert needed"}
            </div>

            {/* Case ID */}
            <p className="case-id">Case ID: {result.case_id}</p>

            {/* Helpline */}
            <div className="helpline">
              🆘 National Cyber Crime Helpline: <strong>1930</strong>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        Built with IBM Bob · watsonx Orchestrate ·{" "}
        <a href="https://github.com/victorysingh/Scamshield" target="_blank" rel="noreferrer">
          GitHub
        </a>
      </footer>
    </div>
  );
}
