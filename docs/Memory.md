# Memory — SchemeSaathi Build Log

A running log to keep context consistent across the day — especially useful when pasting into an AI coding assistant (e.g. Antigravity) so it stays anchored to decisions already made. Update as you go.

## Project Snapshot
- **Name:** SchemeSaathi
- **One-line pitch:** Give the agent one instruction — "find what I'm eligible for and get my applications ready" — and it autonomously plans, checks eligibility, explains, fills forms, and tracks status for Indian government welfare schemes.
- **Domain / PS:** Agentic AI — PS1 (Autonomous Personal Assistant Agent for Multi-Step Real-World Tasks)
- **Budget:** ₹0 — Groq API (free tier) + LangGraph/CrewAI + Streamlit

## Key Decisions Log
| When | Decision | Reason |
|---|---|---|
| Earlier | Chose SchemeSaathi over other ideas (CareerPilot, RakshaCall, MandiMitra, RentGuard) | Most universally relatable + strongest social-impact/scalability story |
| Earlier | Switched tech stack from Claude API to Groq API | Needed a genuinely free, no-cost option |
| Earlier | Designed 4 agents: Eligibility → Explainer → Form-Fill → Follow-up | Maps naturally to the citizen journey, shows real multi-agent architecture |
| Today | Reframed domain from Open Innovation → **Agentic AI PS1** | No fixed rubric in Open Innovation; PS1's requirements (planning, orchestration, memory, clarification, action log) map directly onto the existing 4-agent design |
| Today | Evaluated Lyzr (low-code agent builder) — **rejected** | Only 20 free credits, not enough for build + iterate + live demo |
| Today | Confirmed idea/domain choice via a second AI (Gemini) as a sanity check | Extra validation before committing to final build |
| Today | Added optional Document Vault — single passphrase, dropdown + "Other" free-text labeling, smart reuse of already-uploaded docs | Addresses real security concern for a government-facing tool; strengthens the "orchestration + memory" story for judges |
| Today | Added git checkpoints after every phase | Antigravity makes autonomous edits — need clean rollback points if an agent change breaks something |

## Open Questions / Not Yet Decided
- Which orchestration library to finalize on — LangGraph vs CrewAI (either is fine; pick based on whichever you get running first).
- Final list of schemes to include in `schemes.json` (target: 10–20 real ones).
- Whether to include a second language beyond Hindi if time permits.

## Known Constraints
- Same-day build — see `Phases.md` for the hour-by-hour plan.
- No real government portal integration — data is curated/mocked.
- No paid tools anywhere in the stack (Lyzr explicitly excluded due to credit limit).
- Domain is Agentic AI PS1, not Open Innovation — all docs and pitch framing must lead with "single instruction → autonomous multi-step agent," not "government scheme tool."

## Reference Files
- `PRD.md` — what we're building, why, and how it maps to PS1's requirements
- `Architecture.md` — how it's built, folder structure, agent responsibilities, action log design
- `Rules.md` — constraints and guardrails for the build
- `Phases.md` — build order and time budget, with PS-critical steps flagged
- `Design.md` — visual identity and UI flow, with the action log as a first-class element
- `SchemeSaathi_Pitch_Deck.pptx` — submission pitch deck (tech stack slide already updated to free stack; domain slide still needs updating to Agentic AI)

## Log (append entries as the day progresses)
- [x] Git initialized + `.gitignore` set up (Phase 0)
- [x] Groq API key obtained
- [x] `schemes.json` drafted (Phase 1)
- [x] Eligibility Agent working in isolation (incl. clarification trigger tested) (Phase 2)
- [x] Explainer Agent working in isolation (incl. Hindi output) (Phase 3)
- [x] Form-Fill Agent working (Phase 4)
- [x] Follow-up Agent working (Phase 5)
- [x] Document Vault working (upload, encrypt, label via dropdown/"Other", reuse-check tested) (Phase 5a)
- [x] Orchestrator: planning + state + error handling + action log wired end-to-end (Phase 6)
- [x] Streamlit UI complete, action log panel visible and live-updating (Phase 7)
- [x] Full demo run tested (incl. one clarification path, one error/retry path) (Phase 8)
- [ ] Demo video recorded
- [ ] Pitch deck domain slide updated to Agentic AI
- [ ] Submission uploaded
