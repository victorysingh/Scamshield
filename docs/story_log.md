# Bob Story Log

Screen-record Bob sessions to accompany this table (required for the submission video).

| Time | Task | What we asked Bob | What Bob produced | What we fixed | Bobcoins used |
|------|------|-------------------|-------------------|---------------|---------------|
| 2026-11-14 21:37 IST | Task 1 — Project scaffold | "Create a Python 3.11 project: folders tools/, tests/, data/, docs/. Add README.md, MIT LICENSE, .gitignore (.venv, .env). Add .bob/rules/scamshield.md with 5 rules. Make the first git commit." | `tools/__init__.py`, `tests/__init__.py`, `data/README.md`, `docs/README.md`, `README.md`, `MIT LICENSE`, `requirements.txt` (pytest≥7.4), `.bob/rules/scamshield.md` — first commit `14c473b`. | `.gitignore` already had `.env` and `.venv` (pre-existing); no other fixes needed. | — |
| 2026-11-14 21:46 IST | Task 2 — Red-flag rules | "Implement `check_red_flags(message)` returning a list of named signals with short reasons. Include tests for each signal." | `tools/check_red_flags.py` — 5 regex signals (otp_or_pin_request, urgency_language, arrest_or_seizure_threat, lookalike_link, remote_access_request); `tests/test_check_red_flags.py` — 33 tests across 7 test classes. | 2 tests failed on first run: (1) urgency pattern used singular `hour` — fixed to `hours?`; (2) lookalike-link pattern required `http://` prefix — added plain-text brand-lookalike branch. All 33 tests passed after fix. Commit `bd14953`. | — |
