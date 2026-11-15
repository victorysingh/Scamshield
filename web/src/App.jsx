import { useEffect, useRef, useState } from "react";
import "./App.css";

const API = "http://localhost:5000";

// ---------------------------------------------------------------------------
// Icons (inline SVG so the page works offline and stays crisp at any size)
// ---------------------------------------------------------------------------
const ICONS = {
  shield: "M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5l-8-3Z",
  check: "m5 12 4.5 4.5L19 7",
  alert: "M12 8v5m0 3.5v.5M10.3 3.9 2.5 17.5A2 2 0 0 0 4.2 20.5h15.6a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z",
  phone: "M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2Z",
  users: "M16 19v-1a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v1M9.5 10a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7ZM21 19v-1a4 4 0 0 0-3-3.9M15.5 3.1a3.5 3.5 0 0 1 0 6.8",
  clipboard: "M9 4h6v3H9zM8 5H6a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V6a1 1 0 0 0-1-1h-2",
  search: "m21 21-4.3-4.3M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14Z",
  refresh: "M4 12a8 8 0 0 1 14-5.3L20 9M20 4v5h-5M20 12a8 8 0 0 1-14 5.3L4 15m0 5v-5h5",
  info: "M12 16v-5m0-3.5V7M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z",
};

function Icon({ name, size = 22, strokeWidth = 2 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={ICONS[name]} />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Text — every visible string, so Kannada mode translates the whole page.
// Kannada strings are a draft: have a native speaker check them before the demo.
// ---------------------------------------------------------------------------
const TEXT = {
  english: {
    langName: "English",
    tagline: "Scam check for senior citizens",
    heroTitle: "Got a suspicious message?",
    heroSub: "Paste it below. ScamShield checks it in seconds and tells you exactly what to do.",
    steps: ["Paste the message", "We check 9 warning signs", "Know what to do"],
    inputLabel: "Your message",
    placeholder: "Paste the SMS, WhatsApp or email message here…",
    pasteBtn: "Paste from clipboard",
    clearBtn: "Clear",
    examples: "Or try an example:",
    samples: ["Fake police / CBI", "Bank KYC scam", "Genuine bank SMS"],
    analyse: "Check this message",
    analysing: "Checking…",
    privacyTip: "Tip: you can remove names and account numbers before pasting.",
    error: "Could not connect to ScamShield. Make sure api.py is running.",
    pasteError: "Could not read the clipboard. Press Ctrl+V in the box instead.",
    headline: { high: "Very likely a scam", medium: "Be careful — this looks suspicious", low: "Looks safe" },
    meter: { low: "Low", medium: "Medium", high: "High" },
    riskWord: "Risk",
    typeLabel: "Type",
    scam: {
      bank_kyc:        "Bank / KYC scam",
      courier_customs: "Courier / customs scam",
      fake_official:   "Fake government official scam",
      prize:           "Fake prize / lottery scam",
      investment:      "Fake investment scam",
      unknown:         "No known scam pattern",
    },
    whatToDo: "What you should do",
    whyTitle: "Why we think so",
    noSigns: "We did not find any warning signs.",
    signal: {
      otp_or_pin_request:       "It asks for your OTP, PIN or password",
      urgency_language:         "It rushes you to act immediately",
      arrest_or_seizure_threat: "It threatens arrest or legal action",
      lookalike_link:           "It has a fake, suspicious or hidden link",
      remote_access_request:    "It asks you to install an app or give control of your phone",
      secrecy_pressure:         "It tells you to keep it secret or stay on a call",
      new_number_claim:         "It claims to be someone you know on a new number",
      money_transfer_request:   "It asks you to send money or pay a fee",
      unrealistic_reward:       "It promises a prize, profit or easy income",
    },
    alertSent: "A family member has been alerted",
    alertSentNote: "Demo only — no real SMS is sent",
    alertNone: "No family alert needed",
    callHelpline: "Call 1930",
    helplineNote: "National Cyber Crime Helpline — free, 24×7",
    checkAnother: "Check another message",
    reference: "Reference",
    footer: ["Built with IBM Bob", "watsonx Orchestrate-ready agent", "English + ಕನ್ನಡ", "Open source · MIT"],
  },
  kannada: {
    langName: "ಕನ್ನಡ",
    tagline: "ಹಿರಿಯ ನಾಗರಿಕರಿಗಾಗಿ ಮೋಸ ಪರಿಶೀಲನೆ",
    heroTitle: "ಅನುಮಾನಾಸ್ಪದ ಸಂದೇಶ ಬಂದಿದೆಯೇ?",
    heroSub: "ಅದನ್ನು ಕೆಳಗೆ ಅಂಟಿಸಿ. ScamShield ಕೆಲವೇ ಕ್ಷಣಗಳಲ್ಲಿ ಪರಿಶೀಲಿಸಿ, ನೀವು ಏನು ಮಾಡಬೇಕು ಎಂದು ತಿಳಿಸುತ್ತದೆ.",
    steps: ["ಸಂದೇಶ ಅಂಟಿಸಿ", "9 ಎಚ್ಚರಿಕೆ ಸೂಚನೆಗಳ ಪರಿಶೀಲನೆ", "ಮುಂದೇನು ಎಂದು ತಿಳಿಯಿರಿ"],
    inputLabel: "ನಿಮ್ಮ ಸಂದೇಶ",
    placeholder: "SMS, WhatsApp ಅಥವಾ ಇಮೇಲ್ ಸಂದೇಶವನ್ನು ಇಲ್ಲಿ ಅಂಟಿಸಿ…",
    pasteBtn: "ಕ್ಲಿಪ್‌ಬೋರ್ಡ್‌ನಿಂದ ಅಂಟಿಸಿ",
    clearBtn: "ಅಳಿಸಿ",
    examples: "ಅಥವಾ ಮಾದರಿ ಪ್ರಯತ್ನಿಸಿ:",
    samples: ["ನಕಲಿ ಪೊಲೀಸ್ / CBI", "ಬ್ಯಾಂಕ್ KYC ಮೋಸ", "ನಿಜವಾದ ಬ್ಯಾಂಕ್ SMS"],
    analyse: "ಈ ಸಂದೇಶವನ್ನು ಪರಿಶೀಲಿಸಿ",
    analysing: "ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ…",
    privacyTip: "ಸಲಹೆ: ಅಂಟಿಸುವ ಮೊದಲು ಹೆಸರು ಮತ್ತು ಖಾತೆ ಸಂಖ್ಯೆಗಳನ್ನು ತೆಗೆದುಹಾಕಬಹುದು.",
    error: "ScamShield ಸಂಪರ್ಕವಾಗಲಿಲ್ಲ. api.py ಚಾಲನೆಯಲ್ಲಿದೆಯೇ ಎಂದು ಪರಿಶೀಲಿಸಿ.",
    pasteError: "ಕ್ಲಿಪ್‌ಬೋರ್ಡ್ ಓದಲಾಗಲಿಲ್ಲ. ಬಾಕ್ಸ್‌ನಲ್ಲಿ Ctrl+V ಒತ್ತಿ.",
    headline: { high: "ಇದು ಬಹುಶಃ ಮೋಸ", medium: "ಎಚ್ಚರ — ಇದು ಅನುಮಾನಾಸ್ಪದವಾಗಿದೆ", low: "ಸುರಕ್ಷಿತವಾಗಿ ಕಾಣುತ್ತದೆ" },
    meter: { low: "ಕಡಿಮೆ", medium: "ಮಧ್ಯಮ", high: "ಹೆಚ್ಚು" },
    riskWord: "ಅಪಾಯ",
    typeLabel: "ಬಗೆ",
    scam: {
      bank_kyc:        "ಬ್ಯಾಂಕ್ / KYC ಮೋಸ",
      courier_customs: "ಕೊರಿಯರ್ / ಕಸ್ಟಮ್ಸ್ ಮೋಸ",
      fake_official:   "ನಕಲಿ ಸರ್ಕಾರಿ ಅಧಿಕಾರಿ ಮೋಸ",
      prize:           "ನಕಲಿ ಬಹುಮಾನ / ಲಾಟರಿ ಮೋಸ",
      investment:      "ನಕಲಿ ಹೂಡಿಕೆ ಮೋಸ",
      unknown:         "ತಿಳಿದಿರುವ ಮೋಸದ ಮಾದರಿ ಇಲ್ಲ",
    },
    whatToDo: "ನೀವು ಏನು ಮಾಡಬೇಕು",
    whyTitle: "ನಾವು ಹೀಗೆ ಹೇಳಲು ಕಾರಣ",
    noSigns: "ಯಾವುದೇ ಎಚ್ಚರಿಕೆಯ ಸೂಚನೆ ಕಂಡುಬಂದಿಲ್ಲ.",
    signal: {
      otp_or_pin_request:       "ನಿಮ್ಮ OTP, PIN ಅಥವಾ ಪಾಸ್‌ವರ್ಡ್ ಕೇಳುತ್ತಿದೆ",
      urgency_language:         "ತಕ್ಷಣ ಕ್ರಮ ಕೈಗೊಳ್ಳುವಂತೆ ಒತ್ತಡ ಹಾಕುತ್ತಿದೆ",
      arrest_or_seizure_threat: "ಬಂಧನ ಅಥವಾ ಕಾನೂನು ಕ್ರಮದ ಬೆದರಿಕೆ ಹಾಕುತ್ತಿದೆ",
      lookalike_link:           "ನಕಲಿ, ಅನುಮಾನಾಸ್ಪದ ಅಥವಾ ಮರೆಮಾಡಿದ ಲಿಂಕ್ ಇದೆ",
      remote_access_request:    "ಆ್ಯಪ್ ಇನ್‌ಸ್ಟಾಲ್ ಮಾಡಲು ಅಥವಾ ನಿಮ್ಮ ಫೋನ್ ನಿಯಂತ್ರಣ ನೀಡಲು ಕೇಳುತ್ತಿದೆ",
      secrecy_pressure:         "ಇದನ್ನು ರಹಸ್ಯವಾಗಿಡಲು ಅಥವಾ ಕರೆಯಲ್ಲೇ ಇರಲು ಹೇಳುತ್ತಿದೆ",
      new_number_claim:         "ಹೊಸ ಸಂಖ್ಯೆಯಿಂದ ನಿಮ್ಮ ಪರಿಚಿತರೆಂದು ಹೇಳಿಕೊಳ್ಳುತ್ತಿದೆ",
      money_transfer_request:   "ಹಣ ಕಳುಹಿಸಲು ಅಥವಾ ಶುಲ್ಕ ಪಾವತಿಸಲು ಕೇಳುತ್ತಿದೆ",
      unrealistic_reward:       "ಬಹುಮಾನ, ಲಾಭ ಅಥವಾ ಸುಲಭ ಆದಾಯದ ಭರವಸೆ ನೀಡುತ್ತಿದೆ",
    },
    alertSent: "ಕುಟುಂಬದ ಸದಸ್ಯರಿಗೆ ಎಚ್ಚರಿಕೆ ನೀಡಲಾಗಿದೆ",
    alertSentNote: "ಡೆಮೊ ಮಾತ್ರ — ನಿಜವಾದ SMS ಕಳುಹಿಸಿಲ್ಲ",
    alertNone: "ಕುಟುಂಬಕ್ಕೆ ಎಚ್ಚರಿಕೆ ಅಗತ್ಯವಿಲ್ಲ",
    callHelpline: "1930 ಗೆ ಕರೆ ಮಾಡಿ",
    helplineNote: "ರಾಷ್ಟ್ರೀಯ ಸೈಬರ್ ಅಪರಾಧ ಸಹಾಯವಾಣಿ — ಉಚಿತ, 24×7",
    checkAnother: "ಇನ್ನೊಂದು ಸಂದೇಶ ಪರಿಶೀಲಿಸಿ",
    reference: "ಉಲ್ಲೇಖ",
    footer: ["IBM Bob ಬಳಸಿ ನಿರ್ಮಿಸಲಾಗಿದೆ", "watsonx Orchestrate-ಸಿದ್ಧ ಏಜೆಂಟ್", "English + ಕನ್ನಡ", "ಮುಕ್ತ ಮೂಲ · MIT"],
  },
};

const SAMPLES = [
  {
    risk: "high",
    text: "CBI cybercrime department: A case filed against your mobile number for money laundering. Cooperate or face arrest. Install AnyDesk and share the ID with our officer immediately.",
  },
  {
    risk: "high",
    text: "Dear customer, your SynthBank account KYC is incomplete. Share your OTP immediately to avoid suspension. Call 99900-00001.",
  },
  {
    risk: "low",
    text: "SynthBank: Rs.1,500 debited from account XX0042 at SynthMart on 14-Nov-2026. Balance: Rs.12,340. If not done by you, call 1800-000-0000.",
  },
];

const RISK_ICON = { high: "alert", medium: "alert", low: "check" };
const RISK_LEVELS = ["low", "medium", "high"];

// Backend verdicts start with an emoji; the banner draws its own icon instead
const stripLeadingSymbols = (s) => (s || "").replace(/^[^\p{L}\p{N}]+/u, "");

export default function App() {
  const [message, setMessage]   = useState("");
  const [language, setLanguage] = useState("english");
  const [result, setResult]     = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");
  const resultRef = useRef(null);
  const inputRef  = useRef(null);

  const t = TEXT[language];

  // The result renders below the fold; bring it into view so a senior
  // doesn't think nothing happened after pressing the button.
  useEffect(() => {
    if (result && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [result]);

  useEffect(() => {
    document.documentElement.lang = language === "kannada" ? "kn" : "en";
  }, [language]);

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
    if (lang === language) return;
    setLanguage(lang);
    // Re-explain the current result in the new language without a second
    // click, and without logging a duplicate case or family alert
    if (result) analyse(lang, false);
  }

  async function pasteFromClipboard() {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setMessage(text);
        setResult(null);
        setError("");
      }
    } catch {
      setError(t.pasteError);
    }
  }

  function loadSample(text) {
    setMessage(text);
    setResult(null);
    setError("");
  }

  function startOver() {
    setMessage("");
    setResult(null);
    setError("");
    window.scrollTo({ top: 0, behavior: "smooth" });
    inputRef.current?.focus({ preventScroll: true });
  }

  return (
    <div className="app">
      {/* ── Hero ─────────────────────────────────────────── */}
      <header className="hero">
        <div className="hero-glow" aria-hidden="true" />
        <div className="container">
          <nav className="topbar">
            <div className="brand">
              <span className="brand-mark"><Icon name="shield" size={22} /></span>
              <span className="brand-name">ScamShield</span>
              <span className="brand-tag">{t.tagline}</span>
            </div>
            <div className="lang-switch" role="group" aria-label="Language / ಭಾಷೆ">
              {["english", "kannada"].map((l) => (
                <button key={l} type="button" aria-pressed={language === l}
                  className={language === l ? "active" : ""} onClick={() => changeLanguage(l)}>
                  {TEXT[l].langName}
                </button>
              ))}
            </div>
          </nav>

          <div className="hero-copy">
            <h1>{t.heroTitle}</h1>
            <p>{t.heroSub}</p>
          </div>

          <ol className="steps">
            {t.steps.map((s, i) => (
              <li key={s}><span className="step-num">{i + 1}</span>{s}</li>
            ))}
          </ol>
        </div>
      </header>

      <main className="container main">
        {/* ── Input ─────────────────────────────────────── */}
        <section className="card input-card">
          <div className="input-head">
            <label htmlFor="message" className="input-label">{t.inputLabel}</label>
            <div className="input-tools">
              <button type="button" className="ghost-btn" onClick={pasteFromClipboard}>
                <Icon name="clipboard" size={18} /> {t.pasteBtn}
              </button>
              {message && (
                <button type="button" className="ghost-btn" onClick={startOver}>{t.clearBtn}</button>
              )}
            </div>
          </div>

          <textarea
            id="message"
            ref={inputRef}
            className="textarea"
            rows={5}
            placeholder={t.placeholder}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />

          <div className="samples">
            <span className="samples-label">{t.examples}</span>
            {SAMPLES.map((s, i) => (
              <button key={i} type="button" className="sample-chip" onClick={() => loadSample(s.text)}>
                <span className={`dot dot-${s.risk}`} aria-hidden="true" />
                {t.samples[i]}
              </button>
            ))}
          </div>

          <button type="button" className="primary-btn" onClick={() => analyse()}
            disabled={loading || !message.trim()}>
            {loading ? <span className="spinner" aria-hidden="true" /> : <Icon name="search" size={22} strokeWidth={2.5} />}
            {loading ? t.analysing : t.analyse}
          </button>

          <p className="privacy-tip"><Icon name="info" size={16} /> {t.privacyTip}</p>
          {error && <p className="error-msg" role="alert">{error}</p>}
        </section>

        {/* ── Result ────────────────────────────────────── */}
        {result && (
          <section ref={resultRef} className={`result risk-${result.risk}`} aria-live="polite">
            <div className="verdict-banner">
              <div className="verdict-icon"><Icon name={RISK_ICON[result.risk] ?? "info"} size={34} strokeWidth={2.5} /></div>
              <div className="verdict-text">
                <h2>{t.headline[result.risk] ?? result.risk}</h2>
                <p>{stripLeadingSymbols(result.verdict)}</p>
              </div>
            </div>

            <div className="meter" aria-label={`${t.riskWord}: ${t.meter[result.risk]}`}>
              {RISK_LEVELS.map((lvl) => (
                <div key={lvl} className={`meter-seg seg-${lvl} ${lvl === result.risk ? "on" : ""}`}>
                  {t.meter[lvl]}
                </div>
              ))}
            </div>

            <div className="result-grid">
              <div className="card todo-card">
                <h3>{t.whatToDo}</h3>
                <p className="todo-text">{result.instruction}</p>
                <p className="type-line">{t.typeLabel}: <strong>{t.scam[result.scam_type] ?? result.scam_type}</strong></p>
              </div>

              <div className="card why-card">
                <h3>{t.whyTitle}</h3>
                {result.signal_count > 0 ? (
                  <ul className="why-list">
                    {result.signals.map((s) => (
                      <li key={s}><span className="why-bullet"><Icon name="alert" size={16} strokeWidth={2.5} /></span>
                        {t.signal[s] ?? s.replace(/_/g, " ")}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="no-signs"><Icon name="check" size={18} strokeWidth={2.5} /> {t.noSigns}</p>
                )}
              </div>
            </div>

            <div className={`family-row ${result.alerted ? "sent" : ""}`}>
              <Icon name="users" size={22} />
              <div>
                <strong>{result.alerted ? t.alertSent : t.alertNone}</strong>
                {result.alerted && <span className="family-note">{t.alertSentNote}</span>}
              </div>
            </div>

            <a className="helpline-btn" href="tel:1930">
              <Icon name="phone" size={24} />
              <span>
                <strong>{t.callHelpline}</strong>
                <small>{t.helplineNote}</small>
              </span>
            </a>

            <button type="button" className="again-btn" onClick={startOver}>
              <Icon name="refresh" size={18} /> {t.checkAnother}
            </button>

            {result.case_id && <p className="case-id">{t.reference}: {result.case_id}</p>}
          </section>
        )}
      </main>

      <footer className="footer">
        <div className="container footer-inner">
          {t.footer.map((f) => <span key={f} className="badge">{f}</span>)}
          <a className="badge badge-link" href="https://github.com/victorysingh/Scamshield" target="_blank" rel="noreferrer">GitHub</a>
        </div>
      </footer>
    </div>
  );
}
