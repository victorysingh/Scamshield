# ScamShield — Presentation Deck
## TechGig IBM Bobathon: Build for Bengaluru
### Submission — November 2026

---

## SLIDE 1 — Title

**ScamShield**
*AI-powered scam detection for senior citizens*

Built with **IBM Bob** · Powered by **watsonx Orchestrate**
Team: @jp · Bengaluru

---

## SLIDE 2 — The Problem

**Senior citizens are the #1 target for financial cyber fraud in India.**

- Over **1,03,488** senior citizens filed financial cyber fraud complaints in 2025
  *(Source: MHA statements reported by ANI, August 2026)*
- Common scams: fake bank KYC calls, fake government officials, courier scams,
  prize lottery, fake investment schemes
- Seniors are targeted because they are less familiar with digital fraud patterns
  and often act alone without a second opinion

**The gap:** By the time a family member finds out, money is already gone.

---

## SLIDE 3 — Our Solution

**ScamShield** analyses a suspicious message in seconds and:

1. 🔍 **Detects** scam signals — urgency language, OTP requests, arrest threats,
   lookalike links, remote access requests
2. 🏷️ **Classifies** the scam type — Bank/KYC, Courier, Fake Official, Prize,
   Investment
3. ⚠️ **Scores** the risk — LOW / MEDIUM / HIGH
4. 🗣️ **Explains** the verdict in plain English or **Kannada** — no jargon,
   one clear action
5. 📲 **Alerts** a trusted family contact automatically on HIGH-risk messages

The senior citizen pastes the message. ScamShield does the rest.

---

## SLIDE 4 — How It Works (Architecture)

```
Senior citizen pastes suspicious message
            |
            v
  watsonx Orchestrate Agent (scamshield-agent)
            |
     calls tools in order:
            |
   +--------+--------+--------+
   |                 |        |
analyse_message  send_family  log_scam
                   _alert      _case
   |
   +-- check_red_flags     (5 signal rules)
   +-- classify_and_score  (5 scam types, 3 risk levels)
   +-- explain_in_language (English + Kannada)
            |
            v
  Verdict + Explanation + Alert displayed in chat
```

**IBM Bob** wrote the pipeline, agent, tools, CLI and web UI (Tasks 1–8).
A final round of bug fixes was written by Claude after our Bobcoins ran out — see Slide 6.
**watsonx Orchestrate** hosts the agent and routes tool calls.

---

## SLIDE 5 — Live Demo

*(Record this section as a screen capture for the video)*

**Demo Message 1 — HIGH RISK (Fake Official):**
> "CBI cybercrime department: A case filed against your mobile number for money
> laundering. Cooperate or face arrest. Install AnyDesk and share the ID with
> our officer immediately."

**ScamShield Output:**
- Risk: **HIGH**
- Type: Fake Government Official Scam
- Signals: urgency language, arrest threat, remote access request
- Verdict: "This message is very likely a scam. Do not respond."
- Action: "Real government agencies never ask for money over SMS. Hang up."
- Family alert: **SENT** (simulated)

---

**Demo Message 2 — LOW RISK (Genuine Bank Transaction):**
> "SynthBank: Rs.1,500 debited from account XX0042 at SynthMart on 14-Nov-2026.
> Balance: Rs.12,340. If not done by you, call 1800-000-0000."

**ScamShield Output:**
- Risk: **LOW**
- Type: No scam pattern detected
- Verdict: "This message looks genuine, but always stay alert."
- No family alert needed.

---

**Demo Message 3 — Kannada Output (Bank/KYC Scam):**
> "Dear customer, your SynthBank account KYC is incomplete. Share your OTP
> immediately to avoid suspension."

**ScamShield Output (Kannada):**
- ⚠️ ಈ ಸಂದೇಶವು ಬಹುಶಃ ಮೋಸದ ಸಂದೇಶ. ಯಾವುದೇ ಮಾಹಿತಿಯನ್ನು ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.
- ಫೋನ್ ಅಥವಾ ಸಂದೇಶದ ಮೂಲಕ ಯಾರಿಗೂ ನಿಮ್ಮ OTP ನೀಡಬೇಡಿ.

---

## SLIDE 6 — IBM Bob Story

**Bob wrote all submitted code. Here is what happened:**

| Session | Task | Bob Produced | What We Fixed |
|---------|------|-------------|---------------|
| Nov 14, 21:37 IST | Project scaffold | Folder structure, README, MIT LICENSE, .bob/rules | Minor: .gitignore already existed |
| Nov 14, 21:46 IST | Red-flag rules | check_red_flags.py — 5 regex signals, 33 tests | 2 test failures: regex patterns fixed for plural hours and plain-text lookalike links |
| Nov 14, 22:14 IST | Classifier, Explainer, Alert/Log, Evaluation | 4 tool files, evaluate.py, 45 synthetic messages, 77 tests passing | 1 fix: Windows cp1252 encoding error in print statements — replaced Unicode box chars with ASCII |
| Nov 15, 18:35 IST | Orchestrate agent, deploy script, demo CLI | agent.yaml, scamshield_tools.py, deploy.py, demo.py | 1 fix: case_id uniqueness — added thread-safe counter for same-microsecond collisions |
| Nov 16, 02:48 IST | Web UI | Flask API + React page | — |

**Bob sessions were screen-recorded throughout.**
All corrections were reviewed and approved before commit.

**After Bob — disclosed:** our Bobcoins ran out. A review then found a genuine
"Do not share this OTP" SMS being flagged HIGH, and CLI flags in the deploy
script that do not exist. Those fixes (plus 6 tests) were written by **Claude
(Anthropic), not Bob**, and reviewed by us. False-alarm rate went 6.7% → 0.0%.

---

## SLIDE 7 — watsonx Orchestrate Integration

**Agent:** `scamshield-agent` (native agent, defined for the ADK)

> **Status — update before submitting:** our watsonx Orchestrate access was still
> awaiting approval at the time of writing, so the agent has not yet been deployed.
> If access arrives, run the deploy and replace this note with a screenshot of the
> agent answering in the Orchestrate chat. If not, say so plainly in the video.

**Three tools registered:**

| Tool | Description |
|------|-------------|
| `analyse_message` | Classify scam type + risk + explain in chosen language |
| `send_family_alert` | Simulate trusted-contact alert for HIGH risk |
| `log_scam_case` | Append case record for accuracy reporting |

**Deployment:** `python orchestrate/deploy.py` — one command reads `.env`,
registers and activates the Orchestrate environment, imports the tools
(with the project as package root), then imports the agent.

**LLM:** Amazon Nova Pro (via watsonx Orchestrate AWS)

---

## SLIDE 8 — Results (Accuracy)

**Synthetic test set — 45 messages (30 scam + 15 genuine)**

| Metric | Value |
|--------|-------|
| **Detection rate** | **93.3%** (28 of 30 scams flagged medium or high) |
| **False-alarm rate** | **0.0%** (0 of 15 genuine messages flagged; was 6.7% before the OTP-warning fix) |
| Test set size | 45 messages |
| Scam types covered | 5 (bank/KYC, courier, fake official, prize, investment) |
| Signals detected | 5 (OTP request, urgency, arrest threat, lookalike link, remote access) |

⚠️ *This is a synthetic test set. Results do not represent production accuracy.*
*The dataset was created specifically for this hackathon using made-up names,*
*phone numbers and links — no real personal data.*

**Missed cases (2/30):** Both were investment scam messages with no strong
signal keywords — a watsonx.ai Granite model call (stubbed in code) would
catch these in production.

---

## SLIDE 9 — Privacy & Safety Design

Hackathon rule 8 requires safety projects to address privacy, security and
human review. ScamShield does all three:

**Privacy**
- Zero real personal data in code, tests or datasets
- `.env` credentials never read or printed in logs
- Messages are never sent to external services in the current implementation

**Security**
- No credentials hard-coded — all read from environment variables
- No network calls in the core pipeline — works fully offline
- Audit log (`data/cases.jsonl`) uses only synthetic message text

**Human Review**
- Every HIGH-risk verdict shows the exact signals that triggered it
- The explanation tells the person what to do — not what to decide
- Family alert is simulated (no real SMS) — a human makes the final call
- National Cyber Crime Helpline 1930 shown on every response

---

## SLIDE 10 — Roadmap

What we would build next with more time:

1. **Real watsonx.ai Granite call** — replace the rule stub with a Granite
   3-8B-Instruct model for better coverage of investment and social engineering
   scams
2. **WhatsApp / SMS integration** — seniors receive scams on WhatsApp; a
   webhook to forward messages directly would remove the copy-paste step
3. **Larger labelled dataset** — 500+ messages with community review for a
   statistically meaningful accuracy report
4. **Voice interface** — many seniors prefer speaking; a speech-to-text front
   end with the same pipeline underneath
5. **Kannada dialect tuning** — current Kannada templates are formal; a native
   speaker review and colloquial rewrites would improve comprehension for older
   users

---

## SLIDE 11 — Open Source & Credits

**Repository:** https://github.com/victorysingh/Scamshield
**Licence:** MIT

**Open-source components used:**
- Python 3.11
- pytest 7.4+ (testing)
- ibm-watsonx-orchestrate 2.20.0 (ADK)
- Flask 3 and flask-cors (API)
- React 19 and Vite 8, oxlint (web UI)

**AI-generated content disclosure:**
The code in this repository was generated by IBM Bob and reviewed, tested and
corrected by the team before commit, except the final bug-fix round (OTP-warning
false alarm, risk scoring, deploy-script CLI flags, API input validation, tool
permissions, 6 tests), which Claude (Anthropic) wrote after our Bobcoins ran out.
Claude also assisted with specification writing, test dataset design and
presentation content.
No AI output was submitted without human review.

**Data source:**
Senior citizen cyber fraud figure: ANI / MHA statement, August 2026.
*(https://aninews.in/news/national/general-news/over-1-lakh-senior-citizens...)*

---

## SLIDE 12 — Thank You

**ScamShield**
*Protecting seniors, one message at a time.*

Built with ❤️ in Bengaluru using IBM Bob + watsonx Orchestrate

**National Cyber Crime Helpline: 1930**

---
*End of deck*
