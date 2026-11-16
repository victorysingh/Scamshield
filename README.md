# ScamShield — check before you act

**A scam check for senior citizens in Bengaluru, in English and ಕನ್ನಡ.**
A senior pastes a suspicious SMS or WhatsApp message and, in under a second, gets
a verdict, the reasons behind it and one clear thing to do. If the risk is high, a
family member is alerted, and the 1930 cyber crime helpline is one tap away.

IBM Bobathon: Build for Bengaluru · Theme 3, Safer Communities, Stronger Futures ·
built with **IBM Bob** · agent for **watsonx Orchestrate**
→ Full submission write-up: [docs/SUBMISSION.md](docs/SUBMISSION.md)

**The problem:** scammers impersonate the police ("digital arrest"), banks (KYC/OTP)
and couriers. In 2025, senior citizens in India filed 1,03,488 financial cyber fraud
complaints (MHA figures, as reported by ANI). Seniors have no quick, trustworthy way
to check a message before acting on it.

**What makes it different**
- **Kannada-first, built for seniors:** large text, one action per screen, no jargon.
- **Family in the loop:** high-risk messages bring in a trusted family member
  (simulated in this prototype).
- **Explains, doesn't just score:** shows the warning signs it found, so seniors
  learn to spot the next scam.
- **False alarms treated as failures:** genuine bank SMS and "do not share your OTP"
  warnings are deliberately *not* flagged.
- **Agentic:** an Orchestrate agent analyses the message, decides whether to alert
  the family, and logs the case.

**Impact:** a verdict, its reasons and one action in under a second (about 2 ms through
the API), with no need to call anyone. On 45 synthetic messages it flagged 30/30 scams
with 0/15 false alarms (a small set the rules were tuned on; see [Results](#results)).

**Privacy and human review:** messages are processed locally and never sent to external
services; every verdict shows its reasons; ScamShield advises and the senior decides;
high-risk cases bring in family and the 1930 helpline.

**GitHub:** https://github.com/victorysingh/Scamshield

## Project Structure

```
.
├── tools/          # Core pipeline (each function returns plain JSON)
│   ├── check_red_flags.py      # 9 rule-based warning signals
│   ├── classify_and_score.py   # scam type + risk level
│   ├── explain_in_language.py  # English / Kannada explanation
│   └── alert_and_log.py        # simulated family alert + case log
├── orchestrate/    # watsonx Orchestrate agent (agent.yaml, ADK tools, deploy.py)
├── api.py          # Flask API used by the web UI
├── web/            # React + Vite web UI
├── demo.py         # Command-line demo
├── evaluate.py     # Accuracy report on the synthetic test set
├── tests/          # pytest tests (synthetic data only)
├── data/           # Synthetic test messages and results
├── docs/           # Deck, Bob story log
└── .bob/rules/     # Bob coding rules for this project
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
pytest tests/ -v                     # tests
python evaluate.py                   # detection + false-alarm rates
python demo.py --run-samples         # CLI demo (add --language kannada)

python api.py                        # API on http://localhost:5000
cd web && npm install && npm run dev # web UI (needs api.py running)
```

### Deploy to watsonx Orchestrate

Copy `.env.example` to `.env`, set `WXO_API_KEY` and `WXO_URL`, then:

```bash
python orchestrate/deploy.py
```

## Results

On a synthetic set of 45 messages (30 scam, 15 genuine): **100% detection**
(30/30 flagged medium or high) and **0.0% false alarms** (0/15). The rules were
refined using these same messages, so this is not an independent measure. The set is
small and synthetic, so this is not a production accuracy figure.

## Rules

- Python 3.11 with type hints; every tool has a test.
- Only synthetic data — never real personal data or credentials.
- Every tool returns plain JSON (a `dict`).
- `.env` is never read into logs or printed.

## Credits

Code generated with IBM Bob and reviewed by the team; the final bug-fix round
was written by Claude (Anthropic) after Bobcoins ran out — see
[docs/story_log.md](docs/story_log.md). Open-source components: pytest,
ibm-watsonx-orchestrate, Flask, flask-cors, React, Vite, oxlint.

## License

MIT — see [LICENSE](LICENSE).
