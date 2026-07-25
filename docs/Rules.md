# Rules — SchemeSaathi Build

**Domain:** Agentic AI — PS1. These are the ground rules for building SchemeSaathi today, whether you're coding it yourself or handing tasks to an AI coding assistant (e.g. Antigravity).

## 0. Version Control (Git Checkpoints)
- `git init` immediately in Phase 0, before any code exists.
- Create a `.gitignore` covering: `.env`, `vault/secure_storage/`, `vault/vault_index.json`, `__pycache__/`, `*.pyc` — secrets and encrypted user documents must never be committed.
- Commit at the end of **every phase** in `Phases.md`, not just at the end of the day — if an agent edit in Antigravity breaks something, you want a clean rollback point no more than one phase back.
- Use clear, phase-referenced commit messages, e.g. `git commit -m "Phase 2: Eligibility Agent + clarification logic working"`.
- Before letting Antigravity auto-accept a batch of edits on a risky phase (Orchestrator, Vault), commit first — that's your undo button if the agent's change goes sideways.

## 1. Stay Anchored to the PS Requirements
Every core feature must trace back to one of these five PS requirements — if a feature doesn't serve one of these, it's not a priority today:
1. Task planning and decomposition
2. Multi-tool/API orchestration with error handling
3. Memory and state tracking across steps
4. Clarification only when truly necessary
5. Transparent action log explaining decisions

## 2. Budget & Tooling
- **Zero spend.** Only use free-tier APIs (Groq) and open-source libraries (LangGraph/CrewAI, Streamlit).
- No paid SDKs, no credit-card-gated services, no paid hosting for the demo.
- Do not use Lyzr for this build — confirmed insufficient free credits (20) for a full build-and-demo cycle.

## 3. Scope Discipline
- Build the **narrow end-to-end slice** first (one instruction → one scheme match → filled mock form → status) before adding breadth (more schemes, more languages).
- Do not attempt live government portal integration — mocked/curated data only.
- Resist scope creep: if a feature isn't in `PRD.md`, it doesn't go in today's build.

## 4. Data Integrity
- Only use **real, verifiable** scheme names, eligibility rules, and benefit amounts in `schemes.json` — don't invent fictional schemes, since judges may fact-check.
- Cite the scheme's official source in a code comment if unsure of exact figures.

## 5. Agent Design
- Each agent has **one clear responsibility** (see `Architecture.md`) — don't collapse all logic into a single prompt; the multi-agent handoff is the core innovation story.
- Every agent action must be written to the `action_log` — no silent steps. If it's not logged, judges can't see it, and it won't count toward the PS's transparency requirement.
- Clarification questions must be conditional (only fire when a required field is missing/ambiguous) — don't hardcode a fixed intake form that "asks everything" upfront; that defeats the PS's clarification requirement.
- Wrap every tool/LLM call in error handling with at least one retry — don't let a single failed call crash the whole run.

## 5a. Document Vault Security Rules
- Never hand-roll encryption — use the `cryptography` library's Fernet + PBKDF2HMAC only.
- The passphrase itself is never stored anywhere, in any form — only used transiently to derive the key when needed.
- Decrypted document content must never be written back to disk — decrypt in memory, use, discard.
- Vault contents (labels, filenames) can live in an unencrypted index file since labels alone aren't sensitive, but actual document bytes must always be encrypted at rest.
- Nothing from the vault is ever sent to the Groq API or any external service — it's a purely local feature.
- Wrong-passphrase attempts must fail gracefully (ask user to retry) — never crash the app or leak partial data.

## 6. Language Handling
- Default to English + Hindi for the demo; add more languages only if time permits.
- Always instruct the LLM explicitly on which language to respond in — don't rely on it guessing from context.

## 7. Code Quality (lightweight, hackathon-appropriate)
- Keep functions small and named clearly (`get_eligible_schemes`, `explain_scheme`, `fill_form`, `check_status`).
- No need for full test suites — but do a manual smoke test of the full flow before recording the demo video, including at least one run that triggers the clarification path and one that triggers the retry/error path.
- Keep secrets (API keys) in a `.env` file, never hard-coded or committed.

## 8. Demo Readiness
- Have a **backup plan**: if live LLM calls fail during the live demo (network/rate limits), keep a pre-recorded run or cached example outputs ready.
- The demo must visibly show: (1) the single instruction being given, (2) the plan/decomposition, (3) the action log updating live, (4) a clarification moment, (5) the final filled form + status.
- Rehearse the 5-minute walkthrough at least once before submission.

## 9. Honesty in Submission
- Be accurate about what's mocked vs. real in the Solution Overview (e.g. "form submission is simulated for this demo; real integration is a scaling milestone").
- Judges respond well to honest scoping — don't overclaim live government integration that doesn't exist.
