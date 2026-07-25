# Phases — SchemeSaathi (Same-Day Build)

**Domain:** Agentic AI — PS1. Since today is submission day, phases are scoped in hours. Adjust the clock to your actual remaining time, but keep the order — each phase unblocks the next, and the PS-critical pieces (planning, error handling, action log, clarification) are called out explicitly so they don't get skipped under time pressure.

## Phase 0 — Setup (30–45 min)
- Get a free Groq API key (console.groq.com).
- Set up project folder per `Architecture.md`.
- `pip install streamlit langgraph groq` (or `crewai` if you prefer that orchestrator).
- Confirm a basic "hello world" call to the Groq API works.
- **Git checkpoint:** `git init`, add `.gitignore` (see `Rules.md` §0), commit as "Phase 0: project setup".

## Phase 1 — Data Foundation (30–45 min)
- Write `data/schemes.json` with 10–15 real schemes: PM-KISAN, Ayushman Bharat, PMEGP, National Scholarship Portal schemes, PM Awas Yojana, etc.
- Each entry: eligibility rules, benefits, required documents.
- **Git checkpoint:** commit as "Phase 1: schemes.json data foundation".

## Phase 2 — Eligibility Agent + Clarification Logic (45–60 min)
- Build the function that takes user profile answers + `schemes.json` and returns a ranked shortlist.
- **PS-critical:** add the conditional clarification check — if state/income/occupation is missing or ambiguous, the agent asks a single follow-up question instead of assuming.
- Test in isolation with 2–3 sample profiles, including one incomplete profile that should trigger clarification.
- **Git checkpoint:** commit as "Phase 2: Eligibility Agent + clarification logic".

## Phase 3 — Explainer Agent (30–45 min)
- Take a scheme + language preference → plain-language explanation via Groq LLM call.
- Test with at least one non-English output (Hindi) to confirm multilingual output works.
- **Git checkpoint:** commit as "Phase 3: Explainer Agent".

## Phase 4 — Form-Fill Agent (30 min)
- Template a simple form structure per scheme; auto-fill from user profile answers already collected.
- Keep this mostly rule-based/templated — don't over-engineer with LLM calls here.
- **Git checkpoint:** commit as "Phase 4: Form-Fill Agent".

## Phase 5 — Follow-up Agent (20 min)
- Simple rule-based status tracker + reminder message (can be entirely mocked for the demo).
- **Git checkpoint:** commit as "Phase 5: Follow-up Agent".

## Phase 5a — Document Vault (45–60 min)
- Build `vault/crypto_utils.py`: passphrase → key derivation (PBKDF2) → Fernet encrypt/decrypt functions.
- Build the upload flow: file picker + dropdown (with "Other" → free-text label) → encrypt → save to `secure_storage/` + update `vault_index.json`.
- Build the reuse-check: given a scheme's required documents, check `vault_index.json` for matching labels, return which are present vs. missing.
- Test: upload a dummy "Aadhaar Card", then simulate a scheme needing Aadhaar + Birth Certificate — confirm it only asks for Birth Certificate.
- Test wrong-passphrase handling fails gracefully.
- **Git checkpoint:** commit as "Phase 5a: Document Vault (encrypted local storage)" — double check `.gitignore` is actually excluding `secure_storage/` before this commit.

## Phase 6 — Orchestrator: Planning, State, Error Handling, Action Log (60–75 min)
This is the phase that makes the project genuinely "agentic" rather than a script — don't rush it.
- Connect all four agents in LangGraph/CrewAI, driven by a single high-level instruction.
- Have the orchestrator generate an explicit sub-task plan before executing (log it).
- Maintain shared state (`user_profile`, `matched_schemes`, `chosen_scheme`, `form_data`, `status`) across agents.
- Wrap each agent call in try/except with at least one retry; log failures and fallbacks.
- Append every step (plan, agent start/output, retries, clarification asked) to `action_log`.
- **Git checkpoint:** commit as "Phase 6: Orchestrator wired — planning, state, error handling, action log". Commit *before* this phase too, since it's the riskiest one to let an agent auto-edit.

## Phase 7 — Streamlit UI (45–60 min)
- Single instruction input box + language toggle.
- **Live Action Log panel** — the most visible proof of the PS requirements; make sure it updates as each agent runs.
- Display: clarifying question (if triggered) → shortlist → explanation → filled form → status.
- **Git checkpoint:** commit as "Phase 7: Streamlit UI".

## Phase 8 — End-to-End Test + Demo Prep (30–45 min)
- Run the full flow 2–3 times with different profiles — at least once triggering clarification, once triggering a simulated error/retry.
- Record the 5-minute demo video, narrating the agent's plan, action log, and handoffs explicitly.
- Prepare a backup (screenshots or a recorded run) in case of live-demo hiccups.
- **Git checkpoint:** commit as "Phase 8: end-to-end tested, demo-ready".

## Phase 9 — Submission Packaging (20–30 min)
- Finalize Problem Statement, Solution Overview, Technical Approach docs (see `PRD.md` / `Architecture.md`), confirming Domain = Agentic AI, PS1.
- Attach pitch deck (`SchemeSaathi_Pitch_Deck.pptx`).
- Submit before deadline — leave buffer time for upload issues.
- **Git checkpoint:** final commit + tag, e.g. `git tag submission-v1`.
