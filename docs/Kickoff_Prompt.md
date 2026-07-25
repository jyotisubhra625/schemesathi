# Kickoff Prompt — Paste This Into Antigravity

I'm building **SchemeSaathi** for a same-day hackathon submission (InnovaHack Chapter 1, Domain: Agentic AI, PS1 — Autonomous Personal Assistant Agent for Multi-Step Real-World Tasks). Budget is ₹0 — every tool must be free-tier or open-source.

I've attached six planning files. Please read all of them fully before writing any code, in this order:
1. `docs/PRD.md` — what we're building and why, mapped explicitly to the PS's requirements
2. `docs/Architecture.md` — system design, folder structure, agent responsibilities
3. `docs/Rules.md` — constraints and guardrails (budget, scope, error handling, clarification logic)
4. `docs/Phases.md` — the build order and time budget for today
5. `docs/Design.md` — UI/UX flow, especially the live Action Log panel
6. `docs/Memory.md` — decisions already made; don't re-litigate these

**What I need you to do:**
Follow `docs/Phases.md` in order, starting from Phase 0. Build the project exactly per the folder structure in `Architecture.md`. Do not add features that aren't in `PRD.md` — scope discipline matters more than polish today.

**The most important thing to get right:** this is graded as an *agentic* system, not a simple script. That means:
- The orchestrator must generate an explicit task plan before executing anything.
- Shared state must persist across agent calls (not just function returns).
- Every LLM/tool call needs error handling with at least one retry.
- The agent should ask a clarifying question only when a required field is genuinely missing — not via a fixed upfront form.
- Every step (plan, agent start/output, retries, clarifications) must be written to a visible, live-updating Action Log in the Streamlit UI — this is a graded requirement, not a nice-to-have.

**Tech stack (all free):** Groq API for LLM calls, LangGraph or CrewAI for orchestration, Streamlit for the UI, a local `schemes.json` for data, Python's `cryptography` library for the optional Document Vault. No paid services anywhere.

**Also note:** there's an optional Document Vault feature (encrypted local document storage, single passphrase, dropdown + "Other" free-text labeling, smart reuse of already-uploaded documents) — fully specified in `docs/PRD.md` §5a, `docs/Architecture.md` §2.6, `docs/Design.md` §3a, and `docs/Rules.md` §5a. Build it in Phase 5a, between the Follow-up Agent and the Orchestrator wiring.

Start with Phase 0 (setup — including `git init` and `.gitignore` per `docs/Rules.md` §0) and Phase 1 (`schemes.json` with 10–15 real Indian government schemes), then confirm with me before moving to the agent logic in Phase 2, so I can sanity-check the data before we build on top of it.

**One more thing:** commit to git at the end of every phase, with the exact commit messages given in `docs/Phases.md` (e.g. "Phase 2: Eligibility Agent + clarification logic"). Before making risky autonomous edits — especially in Phase 6 (Orchestrator) and Phase 5a (Document Vault) — commit first so there's a clean rollback point if something breaks.
The GitHub remote is already set up and authenticated at https://github.com/jyotisubhra625/schemesathi.git — commit and push after every phase, using the exact commit messages given in Phases.md.
