# ScamShield BLR: Bob Build Plan and Submission Checklist

Nov 15, 2026 · @jp

Submit by Nov 16, 2026 at 9:00 AM IST, per the TechGig extension email; confirm the new deadline shows on the TechGig portal before relying on it, because I could only see the email text.

## 1. Rules that bind us

Taken from the official rules text on the TechGig page. Read the originals before submitting.

- **Both IBM products are required.** Submissions must demonstrate use of IBM Bob and IBM watsonx Orchestrate (rule 8.1).
- **Fresh Code Rule.** All submitted code must be written during the Hackathon Period. Designs, user flows and datasets may be prepared earlier (rule 7).
- **Prohibited data.** No payment-card data, government IDs, children's data, regulated health data, biometric data or credentials in the Submission (rule 8.3). Do not paste personal data into any AI tool (rule 8.6). We use synthetic messages only.
- **Safety projects need privacy, security and human review** in the design (general term 08).
- **Source repo** must be available free of charge, with no restrictions that block review (rule 6.2). Submissions fall under MIT open-source terms (general term 10), so add an MIT licence.
- **Credit and disclose.** Credit contributors and list open-source components (rules 6.6, 9.3). AI-generated content must be reviewed by us and we are responsible for it (rule 8.2).
- **One submission per team**, and it is final once submitted (rules 4.4, 6.4). Written in English (rule 6.2).
- **Eligibility.** 18+ and a legal resident of Bengaluru (rule 2.1). For the Student Innovation Award, every team member must be an enrolled student with proof (rule 10.2.1).

## 2. What must be submitted

- [ ] Problem statement and detailed solution description
- [ ] Working prototype built with IBM Bob, using watsonx Orchestrate
- [ ] Source code repository (public or reviewer-accessible, MIT licence)
- [ ] Presentation deck or document
- [ ] Video demonstration (check the portal for the maximum length)
- [ ] Bob story and one measurable impact figure, inside the deck and video

Judging is 5 points each for Completeness and Feasibility, Creativity and Innovation, Design and Usability, and Effectiveness and Efficiency, 20 in total. Ties are broken by Completeness and Feasibility first, so a finished, working demo matters most.

## 3. Who does what

- **Bob builds all submitted code.** The rules require a prototype built with Bob and a Bob story, so Claude does not write code that goes into the repo.
- **Claude (this chat) writes the spec, test messages, deck text, problem statement and video script.** You review everything.
- **You run Bob and watsonx Orchestrate,** commit often so the history shows work inside the Hackathon Period, record the video, and submit.

## 4. Scope for the time left

Build only this. Everything else goes in the deck as the future roadmap.

- Text-only message analysis: scam type, risk (low, medium, high), reasons
- Explanation in English and Kannada
- Simulated trusted-contact alert (no real SMS)
- One watsonx Orchestrate agent that calls our Python tools
- A labelled synthetic test set and one accuracy figure
- Optional, only if hours remain: a one-page web interface

## 5. Architecture in one view

1. Senior pastes a suspicious message into the watsonx Orchestrate chat, or the optional web page.
2. The **Orchestrate agent** receives it and calls our tools.
3. **Tool `check_red_flags`** runs rule checks: OTP or PIN request, urgency, threats of arrest or seizure, lookalike links, requests for remote access.
4. **Tool `classify_and_score`** combines the rule results with the model's judgement into scam type and risk level.
5. **Tool `explain_in_language`** writes a plain explanation and one clear instruction in English or Kannada.
6. **Tool `alert_trusted_contact`** creates a short alert for the family contact on high risk (simulated).
7. **Tool `log_case`** stores the result in a local file for the accuracy report.

Tools are Python functions exposed to Orchestrate through the Agent Development Kit, which uses a `@tool` decorator and a YAML agent specification. If connecting a web page to Orchestrate takes too long, demo directly in the Orchestrate chat; it still shows both required products.

## 6. Bob task specs

Paste one at a time into Bob. Review its output before moving on. Each has an acceptance check so we know when to stop.

1. **Project scaffold.** Create a Python project with folders for tools, tests, data and docs, a README, an MIT LICENSE and a `.bob/rules` file. *Done when:* tests run and the repo installs from a fresh clone.
2. **Red-flag rules.** Implement `check_red_flags(message)` returning a list of named signals with short reasons. Include tests for each signal. *Done when:* all tests pass.
3. **Classifier and scorer.** Implement `classify_and_score(message)` returning scam type and low, medium or high risk, combining rules with a model call. *Done when:* it runs on the test set and writes results to a file.
4. **Explainer.** Implement `explain_in_language(result, language)` for English and Kannada, with one plain instruction and no jargon. *Done when:* a native Kannada reader approves three samples.
5. **Alert and log tools.** Implement `alert_trusted_contact` (simulated, writes to a file) and `log_case`. *Done when:* a high-risk message produces an alert record.
6. **Orchestrate agent.** Generate the watsonx Orchestrate agent YAML and import the tools through the ADK. *Done when:* pasting a message in the Orchestrate chat returns the verdict, explanation and alert.
7. **Evaluation script.** Run the test set and print detection rate and false-alarm rate with the set size. *Done when:* one command prints both numbers.
8. **Optional web page.** Large-text single page that sends a message and shows the result. *Done when:* the demo flow works end to end.

**Bobcoin budget.** The trial gives 40 Bobcoins for 30 days; some pages now say 50. One third-party report put a full code-modernization task at about 4 Bobcoins, so these eight tasks could use roughly 25 to 35. That is an estimate. Check usage in Bob after task 2 and trim scope if it runs high.

## 7. Content for `.bob/rules/scamshield.md`

```markdown
# ScamShield BLR rules for Bob
- Python 3.11, type hints, small functions, a test for every tool.
- Never include real personal data, phone numbers, card numbers or government IDs. Use obvious placeholders.
- Messages are synthetic. Do not log or send any real message anywhere.
- High-risk results must support human review: show the reasons and let a person decide.
- Every tool returns plain JSON that the Orchestrate agent can read.
- Keep code readable; comment why, not what.
- Never hard-code credentials. Read them from environment variables.
```

## 8. Test set and impact figure

- Build **40 to 60 synthetic messages**: roughly half genuine (bank statements, OTP notices, delivery updates) and half scams across bank/KYC, courier or customs, fake official, prize and investment types. Use placeholders for names, numbers and links.
- Report **detection rate** (scams flagged high or medium) and **false-alarm rate** (genuine messages flagged), with the exact set size, on the slide and in the video.
- State plainly that the set is synthetic and small. Do not claim production accuracy.

## 9. Bob story log

Keep this table open while building and screen-record the Bob sessions.

| Time | Task | What we asked Bob | What Bob produced | What we fixed | Bobcoins used |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## 10. Time plan, working back from the deadline

Exact hours depend on when you start. Aim to submit a complete version by 7:00 AM and keep the last two hours as buffer.

1. **First hour:** confirm the extension on the portal, get Bob and watsonx Orchestrate access (check TechGig emails first; otherwise start the free trials), create the repo with MIT licence, install the ADK.
2. **Next block:** Bob tasks 1 to 3, then freeze scope.
3. **Next block:** Bob tasks 4 to 6, get the Orchestrate agent answering one message end to end.
4. **Next block:** task 7 evaluation, then record Bob screen sessions while testing.
5. **Content block (parallel, Claude helps):** problem statement, solution description, deck, video script.
6. **Final block:** record video, upload repo link, deck and video, submit, then check the portal shows a complete submission.

## 11. Video script (about 3 minutes, adjust to the portal limit)

1. **Problem:** who is scammed and why, with a sourced figure. Seniors filed 1,03,488 financial cyber fraud complaints in 2025, per MHA statements reported by ANI.
2. **Live demo:** paste one scam and one genuine message; show verdict, Kannada explanation, family alert.
3. **Bob story:** show two or three real Bob sessions and what we corrected.
4. **Orchestrate:** show the agent and its tools.
5. **Impact:** detection and false-alarm rates with set size, then the roadmap.

## 12. Risks

- **Extension not confirmed on the portal.** Check first; if it shows the old deadline, email customercare@techgig.com immediately.
- **Orchestrate setup eats hours.** Fall back to the Orchestrate chat for the demo and drop the web page.
- **Bobcoins run out.** Spend on tasks 2, 3 and 6 first; write simple parts by hand only if the rules allow, and note it in the Bob story. Do not hide it.
- **Kannada quality.** Have a native speaker check the three demo samples.
- **Overclaiming.** Judges can inspect the repo and history (rule 10.5). Say exactly what was built.

## Sources

- TechGig IBM Bobathon: Build for Bengaluru rules and terms, as pasted by the team (not re-opened by me, since the site blocks my tools)
- [IBM Bob free trial](https://bob.ibm.com/trial) and [Bobcoins docs](https://bob.ibm.com/docs/ide/account/bobcoins)
- [watsonx Orchestrate Agent Development Kit docs](https://developer.watson-orchestrate.ibm.com/_releases/1.15.0/getting_started/installing)
- [watsonx Orchestrate ADK tutorial on IBM Developer](https://developer.ibm.com/tutorials/getting-started-with-watsonx-orchestrate/)
- [ANI: senior citizens and women cyber fraud complaints, 2025](https://aninews.in/news/national/general-news/over-1-lakh-senior-citizens-463-lakh-women-lodged-financial-cyber-fraud-complaints-amounting-to-rs-7769-crore-in-2025-govt20260805175125/)
