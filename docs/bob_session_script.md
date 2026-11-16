# ScamShield — Bob Build Session Script
### For video recording · recreates the real build in chronological order

> **How to use this:**
> Open Bob in your browser. Type each "YOU →" prompt exactly as written.
> Wait for Bob to respond (or paste the shown response if re-recording).
> The "WHAT BOB PRODUCES" boxes show the real output from the actual session.
> The "FIX" boxes show what you corrected before moving on.
> Record your screen the whole time.

---

## SESSION 1 · 2026-11-14 21:37 IST
### Task 1 — Project Scaffold

---

**YOU →**
```
Create a Python 3.11 project for a scam-detection tool called ScamShield.

I need:
- Folders: tools/, tests/, data/, docs/
- tools/__init__.py and tests/__init__.py (empty)
- data/README.md and docs/README.md (one-line placeholders)
- README.md with project name, one-line description, and a setup block
- MIT LICENSE
- .gitignore with .venv/ and .env
- requirements.txt with pytest>=7.4
- .bob/rules/scamshield.md with these rules:
  1. Python 3.11, type hints, small functions, a test for every tool.
  2. Never include real personal data, phone numbers, card numbers or government IDs.
  3. Messages are synthetic. Do not log or send any real message anywhere.
  4. High-risk results must support human review: show the reasons.
  5. Every tool returns plain JSON that an Orchestrate agent can read.
  6. Never hard-code credentials. Read from environment variables.

Then make the first git commit with message "chore: project scaffold".
```

---

**WHAT BOB PRODUCES:**

```
tools/__init__.py          ← empty
tests/__init__.py          ← empty
data/README.md             ← "Synthetic test messages — never real data."
docs/README.md             ← "Docs folder."
README.md                  ← project title + setup block
LICENSE                    ← MIT, 2026, your name
.gitignore                 ← .venv/ .env __pycache__/ *.pyc
requirements.txt           ← pytest>=7.4
.bob/rules/scamshield.md   ← 6 rules as above
```

Git output:
```
[main (root-commit) 14c473b] chore: project scaffold
 9 files changed, 47 insertions(+)
```

---

**YOU (reviewing):** ✅ All files created. Tests run with `pytest tests/ -v` — 0 collected, 0 errors. Moving on.

---

---

## SESSION 2 · 2026-11-14 21:46 IST
### Task 2 — Red-Flag Rules

---

**YOU →**
```
Implement tools/check_red_flags.py for ScamShield.

Function signature:
  def check_red_flags(message: str) -> dict

It must detect these 5 named signals using regex:
1. otp_or_pin_request  — message asks recipient to share OTP, PIN or password
2. urgency_language    — time-pressure words (urgent, immediately, within N hours, act now, expires, deadline, today only)
3. arrest_or_seizure_threat — threatens arrest, legal action, asset seizure
4. lookalike_link      — URL mimicking a trusted brand or using suspicious TLD
5. remote_access_request — asks to install AnyDesk, TeamViewer, screen share, install app

Return:
{
  "flagged": true,
  "signals": [
    {"name": "urgency_language", "reason": "Message uses time-pressure..."},
    ...
  ],
  "count": 2
}

Also write tests/test_check_red_flags.py with at least one positive and one
negative test per signal. Use synthetic messages only.
```

---

**WHAT BOB PRODUCES:**

```python
# tools/check_red_flags.py  (excerpt — 5 compiled regex patterns, check_red_flags function)
# tests/test_check_red_flags.py  — 33 tests across 7 test classes
```

---

**YOU (running tests):**
```
pytest tests/ -v
```

**PYTEST OUTPUT — 2 FAILURES:**
```
FAILED tests/test_check_red_flags.py::TestUrgency::test_urgency_hour
FAILED tests/test_check_red_flags.py::TestLookalike::test_plain_text_brand
```

**YOU →**
```
Two tests are failing:

1. test_urgency_hour — message "Act within 1 hour" is not matching. The pattern
   uses `hours` (plural only). Fix it to match both "hour" and "hours".

2. test_plain_text_brand — message "visit paypa1.com to verify" has no http://
   prefix, so the lookalike pattern misses it. Add a plain-text branch that
   matches brand lookalike domains without requiring http.
```

**WHAT BOB PRODUCES:**

```python
# Fix 1: urgency pattern changed from \bhours\b to \bhours?\b
# Fix 2: added plain-text lookalike branch:
#   |\b(paypa1|g00gle|amaz0n|yah00|micros0ft|netf1ix)\.(com|net|org|in)\b
```

**YOU (re-running):**
```
pytest tests/ -v
```
```
33 passed in 0.14s  ✅
```

**YOU:** Committing.
```
git add -A && git commit -m "feat: check_red_flags with 33 tests (fix urgency + lookalike)"
```
```
[main bd14953] feat: check_red_flags ...
```

---

---

## SESSION 3 · 2026-11-14 22:14 IST
### Tasks 3 + 4 + 5 + 7 — Classifier, Explainer, Alert/Log, Evaluation

---

**YOU →**
```
Now build three more tools and an evaluation script for ScamShield.

1. tools/classify_and_score.py
   Function: classify_and_score(message: str) -> dict
   - Call check_red_flags internally
   - Detect scam type from keywords: bank_kyc, courier_customs, fake_official,
     prize, investment, unknown
   - Compute risk: 0 signals → low, 1 signal → medium, 2+ → high
   - Escalate to high if arrest_or_seizure_threat or remote_access_request present
   - Return: scam_type, risk, flagged, signals, reasons, signal_count

2. tools/explain_in_language.py
   Function: explain_in_language(result: dict, language: str) -> dict
   - Supported languages: "english", "kannada"
   - One verdict sentence per risk level
   - One plain instruction per scam type
   - Full Kannada translations for all templates
   - Return: language, verdict, instruction, risk, scam_type

3. tools/alert_and_log.py
   Two functions:
   a. alert_trusted_contact(result: dict, contact_name: str) -> dict
      - Only alert if risk == "high"
      - Simulate by writing to data/alerts.jsonl
      - Return: alerted, contact_name, risk, message_sent, timestamp
   b. log_case(message: str, result: dict, label: str) -> dict
      - Append to data/cases.jsonl
      - Generate a unique case_id
      - Return: logged, case_id, timestamp, risk, scam_type, label

4. data/test_messages.json
   45 synthetic messages: 30 scam (6 each of bank_kyc, courier_customs,
   fake_official, prize, investment) and 15 genuine (bank OTP notice, delivery
   update, bill reminder, etc.). Use fake names and numbers only.

5. evaluate.py
   Load test_messages.json, run classify_and_score on each, print:
   - Detection rate (scams flagged medium or high / total scam)
   - False-alarm rate (genuine flagged / total genuine)
   - Set size

6. Tests for each new tool in tests/ — synthetic data only.
```

---

**WHAT BOB PRODUCES:**

```
tools/classify_and_score.py    ← classifier + risk scorer
tools/explain_in_language.py   ← English + Kannada templates for all 6 scam types
tools/alert_and_log.py         ← simulated alert + JSONL case log
data/test_messages.json        ← 45 synthetic messages with labels
evaluate.py                    ← detection + false-alarm report
tests/test_classify_and_score.py
tests/test_explain_in_language.py
tests/test_alert_and_log.py
```

**YOU (running):**
```
pytest tests/ -v
```
```
77 passed in 0.31s  ✅
```

```
python evaluate.py
```

**OUTPUT:**
```
ScamShield Evaluation
---------------------
Messages : 45  (30 scam, 15 genuine)
Detection rate  : 93.3%  (28/30 flagged medium or high)
False-alarm rate: 6.7%   (1/15 genuine flagged)
```

**YOU (Windows terminal error):**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2014'
```

**YOU →**
```
evaluate.py crashes on Windows with a UnicodeEncodeError on the box-drawing
characters (—, →, ─). Replace them with plain ASCII equivalents so it runs
on cp1252 terminals.
```

**WHAT BOB PRODUCES:**
```python
# Replaced: "—" → "-", "→" → "->", "─" → "-"
```

**YOU (re-running):**
```
python evaluate.py
```
```
ScamShield Evaluation
---------------------
Messages : 45  (30 scam, 15 genuine)
Detection rate  : 93.3%  (28/30 flagged medium or high)
False-alarm rate: 6.7%   (1/15 genuine flagged)
```
✅ Committing.
```
git add -A && git commit -m "feat: classify, explain, alert/log, evaluate, 77 tests"
```
```
[main df411b1] feat: classify, explain, alert/log, evaluate, 77 tests
```

---

---

## SESSION 4 · 2026-11-15 18:35 IST
### Task 6 — watsonx Orchestrate Agent

---

**YOU →**
```
Create the watsonx Orchestrate ADK integration for ScamShield.

1. orchestrate/tools/scamshield_tools.py
   Three @tool functions wrapping our pipeline:
   a. analyse_message(message: str) -> dict
      Runs check_red_flags + classify_and_score + explain_in_language (English)
      + alert_trusted_contact + log_case in one call.
      Returns the full result.
   b. explain_message(message: str, language: str) -> dict
      Re-runs explain_in_language on an existing result for Kannada.
   c. get_case_log() -> dict
      Returns the last 5 entries from data/cases.jsonl.

2. orchestrate/agent.yaml
   ADK agent spec: name ScamShield, description, model ibm/granite-3-8b-instruct,
   instructions to call analyse_message first, then explain if language is Kannada.

3. orchestrate/deploy.py
   Script using ADK CLI calls:
     wxo env add / env activate
     wxo tools import -k python -p orchestrate/tools/
     wxo agents import -f orchestrate/agent.yaml
   Mask the API key in output. Never bundle .env.

4. demo.py
   CLI script: python demo.py --run-samples
   Runs 3 sample messages (1 high scam, 1 medium scam, 1 genuine) and
   prints the result neatly. Add --language kannada flag.
```

---

**WHAT BOB PRODUCES:**

```
orchestrate/__init__.py
orchestrate/tools/scamshield_tools.py   ← 3 @tool functions
orchestrate/agent.yaml                  ← ADK agent spec
orchestrate/deploy.py                   ← deploy script
demo.py                                 ← CLI demo
```

**YOU (testing):**
```
python demo.py --run-samples
```

**Output (excerpt):**
```
Message 1 of 3
--------------
Text    : "Dear Customer, your SBI account has been suspended. Share your OTP
           immediately to reactivate. Visit sbi-secure.xyz now."
Risk    : HIGH
Type    : bank_kyc
Signals : otp_or_pin_request, urgency_language, lookalike_link
Verdict : This message is very likely a scam. Do not respond or share any information.
Alert   : [SIMULATED ALERT to Family Member] A HIGH-RISK bank kyc message was detected...
```

**BUG FOUND — case ID collision:**
```
CASE-20261115183501000000-0001
CASE-20261115183501000000-0001   ← duplicate!
```

**YOU →**
```
Case IDs are colliding when two messages are processed within the same
microsecond. Add a thread-safe monotonic counter to make each case_id unique.
```

**WHAT BOB PRODUCES:**
```python
# Added _counter_lock + _case_counter + _next_counter() to alert_and_log.py
# case_id now: f"CASE-{timestamp}-{_next_counter():04d}"
```

✅ Fixed. Committing.
```
git add -A && git commit -m "feat: orchestrate agent, deploy script, demo"
```
```
[main 67738ff] feat: orchestrate agent, deploy script, demo
```

---

---

## SESSION 5 · 2026-11-16 02:48 IST
### Task 8 — Web UI

---

**YOU →**
```
Add a web interface for ScamShield.

1. api.py  (Flask, port 5000)
   - POST /analyse  — body: {"message": "...", "language": "english"}
     Runs the full pipeline, returns the classify_and_score +
     explain_in_language result as JSON. 400 on non-string input.
   - GET  /health   — returns {"status": "ok"}
   - CORS enabled for localhost:5173 (Vite dev server)

2. web/  — React + Vite app
   - Single page, large text (accessible for seniors)
   - Paste area for the message
   - English / Kannada toggle
   - "Check this message" button
   - Risk badge: colour-coded LOW / MEDIUM / HIGH
   - Warning signals listed in plain words
   - Family alert box shown on HIGH risk
   - 3 sample messages the user can click to load

Add flask and flask-cors to requirements.txt.
```

---

**WHAT BOB PRODUCES:**

```
api.py                     ← Flask app, /analyse + /health
web/package.json           ← React 18 + Vite
web/src/App.jsx            ← full single-page UI
web/src/App.css            ← styles
web/index.html
web/vite.config.js
```

**YOU (testing API):**
```
python api.py
curl -X POST http://localhost:5000/analyse \
  -H "Content-Type: application/json" \
  -d '{"message":"Your parcel is held at customs. Pay clearance fee at bit.ly/abc123"}'
```

**Response:**
```json
{
  "scam_type": "courier_customs",
  "risk": "high",
  "flagged": true,
  "verdict": "This message is very likely a scam. Do not respond or share any information.",
  "instruction": "Do not pay any fee through a link in a message. Contact the courier company directly..."
}
```

**YOU (testing web UI):**
```
cd web && npm install && npm run dev
```
Open http://localhost:5173 — UI loads ✅

Committing:
```
git add -A && git commit -m "feat: Flask API + React web UI"
```
```
[main 55222a6] feat: Flask API + React web UI
```

---

---

## END OF BOB SESSIONS

> At this point Bobcoins were exhausted. Final bug-fixes (detection accuracy,
> deploy script, UI accessibility) were done by Claude and are fully disclosed
> in `docs/story_log.md` and in the presentation deck.

---

## FINAL STATE (after all fixes)

```
pytest tests/ -v     →  98 tests pass
python evaluate.py   →  Detection rate: 100%  |  False-alarm rate: 0.0%
                        (45 messages: 30 scam, 15 genuine — synthetic set)
```

---

## VIDEO SHOT LIST

| Shot | What to show | Duration |
|------|-------------|----------|
| 1 | This script open + Bob chat window side by side | 10 s |
| 2 | Type Task 1 prompt → Bob creates files → `pytest` passes | 1 min |
| 3 | Type Task 2 prompt → Bob writes check_red_flags → 2 test failures → fix prompt → 33 pass | 2 min |
| 4 | Type Task 3 prompt → Bob writes 3 tools + 77 tests → `evaluate.py` output | 2 min |
| 5 | Type Task 6 prompt → `demo.py --run-samples` output showing HIGH risk verdict | 1 min |
| 6 | Type Task 8 prompt → open http://localhost:5173, paste scam message, show badge | 1 min |
| 7 | Paste Kannada message, toggle Kannada, show Kannada verdict | 30 s |
| 8 | `python evaluate.py` final output: 100% detection, 0% false alarms | 20 s |
