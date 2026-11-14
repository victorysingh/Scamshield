# ScamShield

A Python 3.11 toolkit for detecting scam and fraud patterns in messages.

## Project Structure

```
.
├── tools/       # Core detection tools (each returns plain JSON)
├── tests/       # pytest tests (one per tool, synthetic data only)
├── data/        # Synthetic datasets for evaluation
├── docs/        # Documentation and design notes
├── .bob/rules/  # Bob coding rules for this project
└── README.md
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run Tests

```bash
pytest tests/ -v
```

## Rules

- All tools use Python type hints.
- Every tool has a corresponding test.
- Only synthetic data is used — never real personal data or credentials.
- Every tool returns plain JSON (a `dict`).
- `.env` is never read or printed.

## License

MIT — see [LICENSE](LICENSE).
