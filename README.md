# ScamShield

**GitHub:** https://github.com/victorysingh/Scamshield

Scam-message detection for senior citizens in Bengaluru. Paste a suspicious
message and ScamShield returns the scam type, a LOW / MEDIUM / HIGH risk level,
the warning signals it found, and a plain explanation in English or Kannada.
HIGH-risk messages trigger a simulated family alert (no real SMS is sent).

Built for the TechGig IBM Bobathon with **IBM Bob** and **watsonx Orchestrate**.

## Project Structure

```
.
├── tools/          # Core pipeline (each function returns plain JSON)
│   ├── check_red_flags.py      # 5 rule-based warning signals
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
