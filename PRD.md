# PRD — SchemeSaathi

**Domain:** Agentic AI
**Problem Statement:** PS1 — Autonomous Personal Assistant Agent for Multi-Step Real-World Tasks

## 1. The PS, Restated
Build an agent that takes **a single high-level instruction** and autonomously:
- breaks it into sub-tasks (planning/decomposition)
- calls multiple tools/APIs (real or simulated) to gather information
- handles failures and retries along the way
- asks for clarification only when truly necessary
- completes the task end-to-end with a **clear, transparent summary of what it did and why**

The flight/hotel example in the PS is illustrative, not prescriptive — the graded requirement is the *pattern*, not the domain. SchemeSaathi applies that exact pattern to a different real-world task: government welfare scheme discovery and filing.

## 2. The Problem We're Solving
India has 1,000+ central and state welfare schemes, but most eligible citizens never claim them due to:
- **Awareness gap** — schemes are scattered across dozens of portals with no single discovery layer.
- **Eligibility confusion** — income slabs, category rules, and state-specific variations are hard to self-assess.
- **Language & literacy barriers** — documentation is in English/formal Hindi, excluding rural citizens.
- **Paperwork friction** — complex forms cause even eligible applicants to give up midway.

## 3. The Single High-Level Instruction
> "Find out what government schemes I'm eligible for and get my applications ready."

The user gives this once. The agent autonomously plans and executes everything from there — this framing is the core of the pitch and must be visible in the demo, not just implied.

## 4. Target Users
- Rural/semi-urban citizens with low digital literacy
- Farmers, daily-wage workers, students, small business owners, senior citizens
- Secondary user: NGO/CSC (Common Service Centre) staff who assist citizens in filing

## 5. Core Features (MVP for hackathon demo), Mapped to PS Requirements

| PS Requirement | Feature | Owned by |
|---|---|---|
| Task planning & decomposition | On receiving the instruction, agent plans the sub-task sequence (check eligibility → explain → fill → track) before executing | Orchestrator |
| Multi-tool/API orchestration with error handling | Calls scheme knowledge base, LLM (Groq), form templates; retries/handles missing data gracefully | Eligibility, Explainer, Form-Fill Agents |
| Memory & state tracking across steps | Carries user profile + scheme choice across every step; tracks application status afterward | Shared state object + Follow-up Agent |
| Clarification only when necessary | If income/category/state is ambiguous or missing, agent asks — not upfront blanket questioning | Eligibility Agent |
| Transparent action log | Visible, step-by-step log of each agent's action and reasoning, shown in the UI | Frontend + Orchestrator |
| (Security) Sensitive document handling | Optional encrypted local Document Vault, single passphrase, labeled uploads, smart reuse of already-uploaded docs | Form-Fill Agent + Vault module |

## 5a. Document Vault (Encrypted Local Storage) — Additional Feature
Addresses a real judging concern for a government-facing tool: how sensitive documents (Aadhaar, land records, income certificates) are handled.

**How it works, user-facing:**
- **Optional** — a toggle/section the user can ignore entirely if they don't want to store documents.
- **One master passphrase** unlocks the whole vault — the user is never asked for a different passphrase per file.
- **Upload flow:** user picks a document, selects its type from a **dropdown** (Aadhaar Card, PAN Card, Birth Certificate, Land Record, Bank Passbook, Income Certificate, Caste Certificate, Domicile Certificate, etc.). If the correct type isn't listed, they select **"Other"**, which reveals a **free-text box** to type a custom label.
- File is encrypted immediately on upload and stored locally, labeled by the chosen type.
- **Smart reuse:** when a scheme requires certain documents (e.g. Aadhaar + Birth Certificate), the Form-Fill Agent checks the vault first. If a required document is already present (by label), it's used automatically — the user is only asked to upload what's genuinely missing.

**Security requirements:**
- Files encrypted at rest using a proven library (`cryptography`'s Fernet), key derived from the passphrase via PBKDF2 — never hand-rolled crypto.
- Decryption happens in memory only, only when a document is actually needed by an agent; plaintext is never re-written to disk.
- Nothing in the vault is ever sent to the LLM API or any external service — it stays fully local.

## 6. Out of Scope (for today's build)
- Real government API/portal integration
- Aadhaar/DigiLocker auto-fill (mention only as future roadmap)
- Live scraping of all 1,000+ schemes — use a curated dataset of ~15–20 real schemes
- User authentication / persistent accounts
- Payment or transaction handling

## 7. Success Criteria (for demo)
- A judge can give **one instruction** (not a form) and watch the agent visibly plan, then execute, each step.
- The action log is shown on screen — not hidden behind a single loading spinner.
- The agent asks a clarifying question at least once, only when genuinely needed (e.g. ambiguous state/category).
- At least one scheme's explanation is shown in a regional language (e.g. Hindi).
- A mock filled form is shown as output, plus a status/follow-up message.
- If the user has opted into the Document Vault, uploading one labeled document (e.g. Aadhaar) and then requesting a scheme that needs Aadhaar + another document shows the system recognizing the existing upload and only asking for what's missing.

## 8. Constraints
- **Budget: ₹0.** Every tool/library must be free-tier or open-source (Groq API, LangGraph/CrewAI, Streamlit).
- **Time: same-day build.** Favor a working narrow slice over broad but shallow coverage.
