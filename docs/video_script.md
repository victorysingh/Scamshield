# ScamShield — Demo Video Script (about 3 minutes)

Check the maximum video length on the TechGig portal first and trim the
Roadmap section if needed. Narration is about 430 words, roughly 3:05 at a
calm pace.

---

## 0:00–0:20 · The problem

**Screen:** ScamShield home page (hero visible), or a title card.

> In 2025, senior citizens in India filed 1,03,488 financial cyber fraud
> complaints, according to Ministry of Home Affairs figures reported by ANI.
> The message looks official: a police officer, a bank KYC alert, a parcel
> stuck in customs. By the time the family finds out, the money is gone.
> We built ScamShield so a senior can check a message *before* acting on it.

---

## 0:20–1:20 · Live demo

**Shot 1 (0:20) — Fake police / CBI.** Click the *Fake police / CBI* example, then *Check this message*.

> Paste any SMS or WhatsApp message. ScamShield checks it for nine warning
> signs. This one is very likely a scam, and it says exactly why: it rushes
> you, threatens arrest and asks you to install a remote-access app. Then one
> clear thing to do. Because the risk is high, a family member is alerted —
> simulated in this demo, no real SMS — and the 1930 cyber crime helpline is
> one tap away.

**Shot 2 (0:45) — "Digital arrest".** Click *Check another message*, paste:

```
Your Aadhaar is linked to illegal activity. Stay on video call with our officer and do not tell anyone. Transfer funds for verification.
```

> This is a "digital arrest" scam: stay on a video call, tell no one, move
> your money. ScamShield catches the threat, the secrecy pressure and the
> money request.

**Shot 3 (1:00) — Kannada.** Click **ಕನ್ನಡ** at the top right; let the page switch.

> Many seniors in Bengaluru are more comfortable in Kannada. One tap switches
> the whole page and the advice to Kannada.

**Shot 4 (1:10) — Genuine message.** Switch back to English, click *Genuine bank SMS*, then *Check this message*.

> And a genuine bank SMS? Looks safe, no alert. A tool that cries wolf gets
> ignored, so avoiding false alarms matters as much as catching scams.

---

## 1:20–1:50 · watsonx Orchestrate

Record **one** of these, depending on whether your Orchestrate access was approved.

**Version A — agent deployed.** Screen: Orchestrate chat with `scamshield-agent`; paste the digital-arrest message.

> The same tools run as an agent on IBM watsonx Orchestrate. The agent calls
> our three tools — analyse the message, alert the family, log the case —
> and answers in plain language, always ending with the 1930 helpline.

**Version B — access still pending.** Screen: `orchestrate/agent.yaml`, then the `@tool` functions in `orchestrate/tools/scamshield_tools.py`, then `orchestrate/deploy.py`.

> The same three tools are packaged as a watsonx Orchestrate agent using the
> Agent Development Kit: here is the agent definition and the tool functions.
> Our Orchestrate access was still awaiting approval when we recorded this, so
> deployment is ready as one command: `python orchestrate/deploy.py`.

Do not open `.env` on screen.

---

## 1:50–2:30 · The Bob story

**Screen:** `4_bob_session.webm` (about 41 s). Part 1 is the Task 2 prompt re-run in
an empty folder for this video, captioned as a re-run. Part 2 scrolls `docs/story_log.md`.

**Over part 1, the Bob re-run (0:00–0:25 of the clip):**

> IBM Bob built ScamShield task by task: the scaffold, the red-flag rules, the
> classifier, the Kannada explainer, the alert and log tools, the Orchestrate
> agent and the web interface. Here we re-ran the red-flag task for this video:
> Bob writes the rules and 33 tests, and they pass.

**Over part 2, the story-log scroll (0:25–0:41):**

> In the original session on 14 November, two of those tests failed —
> "within 24 hours" wasn't matched, and plain-text lookalike links slipped
> through — and we fixed them together. When our Bobcoins ran out, Claude did
> the final fixes and UI polish, and every change is disclosed in this log.

Do not describe part 1 as the original build: the footage passes 33/33 on the
first try, so the "two tests failed" line belongs over the story log only.

---

## 2:30–2:55 · Results

**Screen:** terminal with large font. Run `pytest tests -q`, then `python evaluate.py`.

> On our synthetic test set of 45 messages — 30 scams and 15 genuine —
> ScamShield flags all 30 scams with zero false alarms, and 98 automated tests
> pass. To be clear: the set is small and synthetic, and our rules were
> refined on it, so this is not a real-world accuracy figure.

---

## 2:55–3:10 · Roadmap and close

**Screen:** home page, or a closing card with the GitHub link.

> Next: a watsonx.ai Granite model for scams the rules miss, a WhatsApp
> number you can forward messages to, voice input, and a larger held-out test
> set reviewed with seniors. ScamShield: check before you act. And if in
> doubt, call 1930.

---

## Recording checklist

- [ ] Confirm the maximum video length on the portal.
- [ ] App running: `python api.py` (project folder) and `npm run dev` (`web/`); open `http://localhost:5173` and hard-refresh (Ctrl+F5).
- [ ] Browser full screen (F11), zoom 110–125%, bookmarks bar hidden, other tabs closed.
- [ ] Notifications off (Windows Focus / Do not disturb).
- [ ] Keep the digital-arrest message in a text file ready to paste — no typing on camera.
- [ ] Terminal font at 18pt or larger for the results section.
- [ ] Never show `.env` or any real phone number, name or account number.
- [ ] Insert real Bob session footage in the Bob story section.
- [ ] Add captions if the editor supports it; it helps judges watching muted.
