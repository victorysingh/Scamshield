import { useEffect, useRef, useState } from "react";
import "./App.css";

const API = "http://localhost:5000";

// Colours chosen for at least 4.5:1 text contrast on their badge backgrounds
const RISK_STYLE = {
  high:   { color: "#b91c1c", bg: "#fdecea", icon: "⚠️" },
  medium: { color: "#b45309", bg: "#fef3e2", icon: "⚠️" },
  low:    { color: "#15803d", bg: "#eafaf1", icon: "✅" },
};

// All visible text, so Kannada mode translates the whole page, not just the verdict.
// Kannada strings are a draft: have a native speaker check them before the demo.
const TEXT = {
  english: {
    tagline: "Instant scam check for senior citizens",
    title: "Paste a suspicious message",
    trySample: "Try a sample:",
    placeholder: "Paste the message here...",
    languageLabel: "Output language:",
    analyse: "Check this message",
    analysing: "Checking…",
    error: "Could not connect to ScamShield. Make sure api.py is running.",
    risk: { high: "HIGH RISK", medium: "MEDIUM RISK", low: "LOW RISK" },
    typeLabel: "Type:",
    scam: {
      bank_kyc:        "Bank / KYC scam",
      courier_customs: "Courier / customs scam",
      fake_official:   "Fake government official scam",
      prize:           "Fake prize / lottery scam",
      investment:      "Fake investment scam",
      unknown:         "No specific scam pattern found",
    },
    signalsTitle: (n) => `Warning signs we found (${n}):`,
    signal: {
      otp_or_pin_request:       "It asks for your OTP, PIN or password",
      urgency_language:         "It rushes you to act immediately",
      arrest_or_seizure_threat: "It threatens arrest, police or legal action",
      lookalike_link:           "It has a fake or suspicious-looking link",
      remote_access_request:    "It asks you to install an app or give control of your phone",
      secrecy_pressure:         "It tells you to keep it secret or stay on a call",
      new_number_claim:         "It claims to be someone you know on a new number",
      money_transfer_request:   "It asks you to send money or pay a fee",
      unrealistic_reward:       "It promises a prize, profit or easy income",
    },
    alertSent: "📲 Family member alerted (demo — no real SMS sent)",
    alertNone: "No family alert needed",
    reference: "Reference",
    helpline: "National Cyber Crime Helpline:",
  },
  kannada: {
    tagline: "ಹಿರಿಯ ನಾಗರಿಕರಿಗಾಗಿ ತಕ್ಷಣದ ಮೋಸ ಪರಿಶೀಲನೆ",
    title: "ಅನುಮಾನಾಸ್ಪದ ಸಂದೇಶವನ್ನು ಇಲ್ಲಿ ಅಂಟಿಸಿ",
    trySample: "ಮಾದರಿ ಸಂದೇಶ:",
    placeholder: "ಸಂದೇಶವನ್ನು ಇಲ್ಲಿ ಅಂಟಿಸಿ...",
    languageLabel: "ಉತ್ತರದ ಭಾಷೆ:",
    analyse: "ಈ ಸಂದೇಶವನ್ನು ಪರಿಶೀಲಿಸಿ",
    analysing: "ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ…",
    error: "ScamShield ಸಂಪರ್ಕವಾಗಲಿಲ್ಲ. api.py ಚಾಲನೆಯಲ್ಲಿದೆಯೇ ಎಂದು ಪರಿಶೀಲಿಸಿ.",
    risk: { high: "ಹೆಚ್ಚಿನ ಅಪಾಯ", medium: "ಮಧ್ಯಮ ಅಪಾಯ", low: "ಕಡಿಮೆ ಅಪಾಯ" },
    typeLabel: "ಬಗೆ:",
    scam: {
      bank_kyc:        "ಬ್ಯಾಂಕ್ / KYC ಮೋಸ",
      courier_customs: "ಕೊರಿಯರ್ / ಕಸ್ಟಮ್ಸ್ ಮೋಸ",
      fake_official:   "ನಕಲಿ ಸರ್ಕಾರಿ ಅಧಿಕಾರಿ ಮೋಸ",
      prize:           "ನಕಲಿ ಬಹುಮಾನ / ಲಾಟರಿ ಮೋಸ",
      investment:      "ನಕಲಿ ಹೂಡಿಕೆ ಮೋಸ",
      unknown:         "ನಿರ್ದಿಷ್ಟ ಮೋಸದ ಮಾದರಿ ಕಂಡುಬಂದಿಲ್ಲ",
    },
    signalsTitle: (n) => `ಕಂಡುಬಂದ ಎಚ್ಚರಿಕೆಯ ಸೂಚನೆಗಳು (${n}):`,
    signal: {
      otp_or_pin_request:       "ನಿಮ್ಮ OTP, PIN ಅಥವಾ ಪಾಸ್‌ವರ್ಡ್ ಕೇಳುತ್ತಿದೆ",
      urgency_language:         "ತಕ್ಷಣ ಕ್ರಮ ಕೈಗೊಳ್ಳುವಂತೆ ಒತ್ತಡ ಹಾಕುತ್ತಿದೆ",
      arrest_or_seizure_threat: "ಬಂಧನ, ಪೊಲೀಸ್ ಅಥವಾ ಕಾನೂನು ಕ್ರಮದ ಬೆದರಿಕೆ ಹಾಕುತ್ತಿದೆ",
      lookalike_link:           "ನಕಲಿ ಅಥವಾ ಅನುಮಾನಾಸ್ಪದ ಲಿಂಕ್ ಇದೆ",
      remote_access_request:    "ಆ್ಯಪ್ ಇನ್‌ಸ್ಟಾಲ್ ಮಾಡಲು ಅಥವಾ ನಿಮ್ಮ ಫೋನ್ ನಿಯಂತ್ರಣ ನೀಡಲು ಕೇಳುತ್ತಿದೆ",
      secrecy_pressure:         "ಇದನ್ನು ರಹಸ್ಯವಾಗಿಡಲು ಅಥವಾ ಕರೆಯಲ್ಲೇ ಇರಲು ಹೇಳುತ್ತಿದೆ",
      new_number_claim:         "ಹೊಸ ಸಂಖ್ಯೆಯಿಂದ ನಿಮ್ಮ ಪರಿಚಿತರೆಂದು ಹೇಳಿಕೊಳ್ಳುತ್ತಿದೆ",
      money_transfer_request:   "ಹಣ ಕಳುಹಿಸಲು ಅಥವಾ ಶುಲ್ಕ ಪಾವತಿಸಲು ಕೇಳುತ್ತಿದೆ",
      unrealistic_reward:       "ಬಹುಮಾನ, ಲಾಭ ಅಥವಾ ಸುಲಭ ಆದಾಯದ ಭರವಸೆ ನೀಡುತ್ತಿದೆ",
    },
    alertSent: "📲 ಕುಟುಂಬದ ಸದಸ್ಯರಿಗೆ ಎಚ್ಚರಿಕೆ ನೀಡಲಾಗಿದೆ (ಡೆಮೊ — ನಿಜವಾದ SMS ಕಳುಹಿಸಿಲ್ಲ)",
    alertNone: "ಕುಟುಂಬಕ್ಕೆ ಎಚ್ಚರಿಕೆ ಅಗತ್ಯವಿಲ್ಲ",
    reference: "ಉಲ್ಲೇಖ",
    helpline: "ರಾಷ್ಟ್ರೀಯ ಸೈಬರ್ ಅಪರಾಧ ಸಹಾಯವಾಣಿ:",
  },
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
  const resultRef = useRef(null);

  const t = TEXT[language];

  // The result card renders below the fold; bring it into view so a senior
  // doesn't think nothing happened after pressing the button.
  useEffect(() => {
    if (result && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [result]);

  async function analyse(lang = language, record = true) {
    if (!message.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API}/analyse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, language: lang, record }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      // A language switch doesn't create a new case, so keep the earlier reference
      setResult((prev) => (record ? data : { ...data, case_id: prev?.case_id ?? null }));
    } catch {
      setResult(null);
      setError(TEXT[lang].error);
    } finally {
      setLoading(false);
    }
  }

  function changeLanguage(lang) {
    setLanguage(lang);
    // Re-explain the current result in the new language without a second click,
    // without logging a duplicate case or family alert
    if (result) analyse(lang, false);
  }

  function loadSample(text) {
    setMessage(text);
    setResult(null);
    setError("");
  }

  const risk = result ? RISK_STYLE[result.risk] ?? RISK_STYLE.low : null;

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <span className="logo">🛡️ ScamShield</span>
          <span className="tagline">{t.tagline}</span>
        </div>
      </header>

      <main className="main">
        <section className="card input-card">
          <h2 className="section-title">{t.title}</h2>

          <div className="samples">
            <span className="samples-label">{t.trySample}</span>
            {SAMPLES.map((s) => (
              <button key={s.label} className="sample-btn" onClick={() => loadSample(s.text)}>
                {s.label}
              </button>
            ))}
          </div>

          <textarea
            className="textarea"
            rows={5}
            placeholder={t.placeholder}
            aria-label={t.title}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />

          <div className="lang-row" role="radiogroup" aria-label={t.languageLabel}>
            <span className="lang-label">{t.languageLabel}</span>
            <label className="lang-option">
              <input type="radio" name="language" value="english" checked={language === "english"}
                onChange={() => changeLanguage("english")} /> English
            </label>
            <label className="lang-option">
              <input type="radio" name="language" value="kannada" checked={language === "kannada"}
                onChange={() => changeLanguage("kannada")} /> ಕನ್ನಡ (Kannada)
            </label>
          </div>

          <button
            className="analyse-btn"
            onClick={() => analyse()}
            disabled={loading || !message.trim()}
          >
            {loading ? t.analysing : t.analyse}
          </button>

          {error && <p className="error-msg" role="alert">{error}</p>}
        </section>

        {result && (
          <section
            ref={resultRef}
            className="card result-card"
            style={{ borderTop: `6px solid ${risk.color}` }}
            aria-live="polite"
          >
            <div className="risk-badge" style={{ background: risk.bg, color: risk.color }}>
              <span className="risk-icon" aria-hidden="true">{risk.icon}</span>
              <span className="risk-label">{t.risk[result.risk] ?? result.risk}</span>
            </div>

            <p className="scam-type">
              <strong>{t.typeLabel}</strong> {t.scam[result.scam_type] ?? result.scam_type}
            </p>

            <div className="verdict-box">
              <p className="verdict">{result.verdict}</p>
              <p className="instruction">{result.instruction}</p>
            </div>

            {result.signal_count > 0 && (
              <div className="signals">
                <p className="signals-title">⚡ {t.signalsTitle(result.signal_count)}</p>
                <ul className="signals-list">
                  {result.signals.map((s) => (
                    <li key={s}>{t.signal[s] ?? s.replace(/_/g, " ")}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className={`alert-box ${result.alerted ? "alert-sent" : "alert-none"}`}>
              {result.alerted ? t.alertSent : t.alertNone}
            </div>

            <div className="helpline">
              🆘 {t.helpline} <strong>1930</strong>
            </div>

            {result.case_id && <p className="case-id">{t.reference}: {result.case_id}</p>}
          </section>
        )}
      </main>

      <footer className="footer">
        Built with IBM Bob · Same detection tools power our watsonx Orchestrate agent ·{" "}
        <a href="https://github.com/victorysingh/Scamshield" target="_blank" rel="noreferrer">
          GitHub
        </a>
      </footer>
    </div>
  );
}
