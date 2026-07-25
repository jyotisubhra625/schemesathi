# Design — SchemeSaathi

**Domain:** Agentic AI — PS1

## 1. Design Principles
- **The action log is the star, not an afterthought.** Since "transparent action log explaining decisions" is a graded PS requirement, it must be a prominent, live-updating UI element — not a hidden console log.
- **One instruction in, not a form.** The entry point should feel like giving an assistant a single command, not filling out a survey — this is core to the PS's premise and should be visually obvious.
- **Clarity over polish.** Judges and low-literacy end-users both need instant comprehension — favor plain language and simple layout over visual flourish.
- **Local, not generic.** Visual and language choices should feel rooted in an Indian civic context rather than a generic SaaS look.

## 2. Visual Identity (carried over from pitch deck)
- **Palette:** deep teal (`#0B3D3F`) for trust/authority, teal (`#028090`) and mint (`#02C39A`) as accents, off-white (`#F4F9F8`) background for readability.
- **Typography:** a serif display face (e.g. Cambria) for headings to feel institutional/trustworthy; a clean sans (e.g. Calibri) for body text and forms.
- **Motif:** soft circular accents + numbered/lettered badges (used for the 4 agents: E, X, F, T) — reuse this in the app UI for consistency with the pitch deck.

## 3. UI Flow (Streamlit)
1. **Instruction screen** — a single input box: *"Tell SchemeSaathi what you need"* (default placeholder: "Find out what government schemes I'm eligible for and get my applications ready.") + a language selector (English/Hindi to start).
2. **Live Action Log panel** — appears immediately after instruction submission, updating step-by-step in real time:
   - "Planning: breaking your request into eligibility check → explanation → form-fill → tracking"
   - "Eligibility Agent: checking your profile against 14 schemes..."
   - "Clarification needed: which state are you in?" (only if triggered)
   - "Explainer Agent: preparing explanation in Hindi..."
   - etc.
3. **Clarification prompt (conditional)** — a simple inline question if the agent lacks a required field, not a blanket upfront form.
4. **Eligibility results** — card-style list of matched schemes, ranked, each with a one-line reason.
5. **Explanation view** — plain-language breakdown per selected scheme, in the chosen language, with a visible "required documents" checklist.
6. **Form-fill preview** — a mock filled-form view (key-value display) with a clear "Simulated for demo" label.
7. **Status tracker** — simple status badge (e.g. "Application Ready" / "Reminder: renew by [date]").

## 3a. Document Vault UI (Optional Feature)
- A clearly separate, optional section — e.g. a collapsible panel titled "Secure Document Vault (optional)" so it never feels mandatory to proceed.
- **First use:** prompt for a passphrase once, with a plain-language note: *"This passphrase unlocks all your stored documents. We don't store it — don't forget it."*
- **Upload control:** file picker + a **dropdown** of common document types (Aadhaar Card, PAN Card, Birth Certificate, Land Record, Bank Passbook, Income Certificate, Caste Certificate, Domicile Certificate) + an **"Other"** option that reveals a free-text label input.
- **Vault contents view:** a simple labeled list of what's already stored (e.g. "✓ Aadhaar Card uploaded"), so the user and the judges can see at a glance what's available for reuse.
- **Smart reuse moment (important for the demo):** when a scheme requires documents, show a line like *"Aadhaar Card — already in your vault ✓"* next to *"Birth Certificate — please upload"* — this visual contrast is what proves the reuse logic is working, make sure it's not buried.

## 4. Why the Action Log Placement Matters
Place it **beside or above** the results, not below/hidden — during the live demo, judges should be able to watch the agent think and act in real time, which is the most direct visual proof that this is an autonomous agent and not a scripted chatbot.

## 5. Accessibility Considerations
- Large, high-contrast text (many end-users may have low digital literacy).
- Avoid jargon in user-facing copy — reserve technical terms for the action log/judges, not the citizen-facing results.
- Language toggle should be prominent and persistent across screens.

## 6. What NOT to Design Today
- No account/login screens.
- No animations or complex transitions — Streamlit's default components are enough.
- No mobile-specific optimization — a desktop browser demo is sufficient for judging.
