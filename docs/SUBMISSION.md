# ScamShield — IBM Bobathon: Build for Bengaluru

**Theme:** 3. Safer Communities, Stronger Futures (senior check-ins and scam awareness)
**Repo:** https://github.com/victorysingh/Scamshield

**One line:** a senior pastes a suspicious SMS or WhatsApp message and, in under a
second, gets a verdict, the reasons behind it and one clear thing to do, in English
or Kannada. On a high-risk message, a family member is alerted.

---

## The problem

**Who it affects:** senior citizens in Bengaluru, and their families.

Scammers impersonate the police ("digital arrest"), banks (KYC/OTP), couriers
(customs fees) and prize schemes. In 2025, senior citizens in India filed
1,03,488 financial cyber fraud complaints (Ministry of Home Affairs figures, as
reported by ANI). These messages are written to look official and to rush the reader.

**What needs to improve:** a senior has no quick, trustworthy way to check a message
*before* acting on it. Today the options are to guess, or to call a family member and
wait. By the time the family finds out, the money is often gone.

## The prototype

A working web app and API, plus an agent ready for watsonx Orchestrate:

1. **Check:** paste a message into a large-text page made for seniors, or tap a sample.
2. **Verdict:** LOW / MEDIUM / HIGH risk, with the scam type (bank/KYC, courier/customs,
   fake official, prize, investment).
3. **Why:** the specific warning signs found, in plain words. There are 9 signals,
   including OTP request, urgency, arrest threat, remote-access app, secrecy
   pressure ("digital arrest") and money-transfer request.
4. **What to do:** one clear instruction, plus a tap-to-call button for the 1930 National
   Cyber Crime Helpline.
5. **Family in the loop:** on HIGH risk, a trusted family member is alerted. In this
   prototype the alert is simulated, and no real SMS is sent.
6. **Kannada:** one tap switches the whole page and the advice to Kannada.

**Agentic AI with watsonx Orchestrate:** the same pipeline is packaged as three ADK tools
(`analyse_message`, `send_family_alert`, `log_scam_case`) in an Orchestrate agent
(`orchestrate/agent.yaml`). The agent analyses the message, decides on its own whether
the risk warrants alerting the family, logs the case, and always ends with the 1930
helpline. Deployment takes one command (`python orchestrate/deploy.py`). Our Orchestrate
instance was still being activated at submission time, so the demo shows the agent
definition rather than a live run.

**Built to be trusted and cheap to run:** detection is explainable (every verdict
shows its reasons), needs no paid model calls, runs offline, and is covered by
98 automated tests.

## What makes it different

- **Kannada-first, built for seniors:** large text, one action per screen and no
  jargon, designed for the people being targeted rather than for tech users.
- **Family in the loop:** high-risk results bring in a trusted person, so the senior
  doesn't have to decide alone.
- **False alarms treated as a failure:** a tool that cries wolf gets ignored. Genuine
  bank SMS and "do not share your OTP" warnings are deliberately *not* flagged.
- **Explains, doesn't just score:** it shows why a message is risky, so the senior
  learns to spot the next scam (scam awareness, not just scam blocking).

## The Bob story

IBM Bob built ScamShield task by task: the project scaffold and coding rules, the
red-flag detector, the classifier, the Kannada explainer, the alert and log tools,
the Orchestrate agent and deploy script, and the web UI and API. We reviewed every
step and fixed issues with Bob along the way. For example, Bob's first red-flag
rules failed 2 of their own 33 tests, `evaluate.py` crashed on Windows terminals,
and case IDs collided within the same microsecond.

When our Bobcoins ran out, we used Claude (Anthropic) for the final review fixes and
UI polish. Every one of those changes is marked "written by Claude, not Bob" in
[`docs/story_log.md`](story_log.md). The Bob clip in our video is the Task 2 prompt
re-run for the recording, and it is captioned as a re-run.

## The impact (measurable outcome)

**Time to a trustworthy answer: from "call someone and wait" to under one second.**
The classifier takes about 0.07 ms per message, and a full check through the API takes
about 2 ms on a laptop. The senior gets a verdict, the reasons and one action
straight away, without needing anyone's help.

Supporting result: on our test set of 45 synthetic messages (30 scams, 15 genuine),
ScamShield flagged **30/30 scams** with **0/15 false alarms**. To be clear, the set is
small and synthetic, and our rules were refined on it, so this is not a real-world
accuracy figure. The next step is a larger held-out set reviewed with seniors.

## Privacy and human review

**Privacy**
- Messages are processed locally and never sent to any external service. The core
  pipeline makes no network calls.
- Only synthetic data is used in code, tests and the demo. The page tells users they
  can remove names and account numbers before pasting.
- Cases are logged only on the local machine (`data/cases.jsonl`, excluded from git).
  For real users we would store a redacted message rather than the full text.
- No credentials are hard-coded, and the deploy script masks the API key and never
  uploads `.env`.

**Human review**
- Every verdict shows the exact signals behind it, so a person can check the reasoning.
- ScamShield advises and does not act: it tells the senior what to do, and the
  senior decides.
- High-risk messages bring in a family member, and the 1930 helpline is one tap away.
- The Orchestrate agent is instructed to recommend human review before any action on
  high-risk messages, and never to ask for personal information.

## Limitations and next steps

- Detection is rule-based. Next: a watsonx.ai Granite model for scam wording the rules
  miss, with the rules kept as an explainable first layer.
- Seniors receive scams on WhatsApp. Next: a WhatsApp number they can forward
  messages to, which removes the copy-paste step.
- Voice input, and a native-speaker review of the Kannada text.
- Live deployment on watsonx Orchestrate once our instance is active.
