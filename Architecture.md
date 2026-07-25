# Architecture — SchemeSaathi

**Domain:** Agentic AI — PS1 (Autonomous Personal Assistant Agent for Multi-Step Real-World Tasks)

## 1. High-Level Flow
```
User gives ONE instruction:
"Find out what government schemes I'm eligible for and get my applications ready."
        │
        ▼
Planner / Orchestrator (LangGraph or CrewAI)
   - Decomposes instruction into sub-tasks
   - Tracks shared state across all steps
   - Writes every decision to the Action Log
        │
   ┌────┼─────────┬──────────────┐
   ▼    ▼          ▼              ▼
Eligibility   Explainer     Form-Fill      Follow-up
  Agent        Agent          Agent          Agent
   │             │              │              │
   └──── Scheme Knowledge Base (schemes.json) ──┘
        │
        ▼
   Transparent Action Log (shown live in UI)
```

## 2. Components

### 2.1 Planner / Orchestrator (the core "agentic" piece)
- **LangGraph** (preferred) or **CrewAI**.
- Receives the single high-level instruction and produces an explicit task plan (list of sub-tasks) before executing anything — this plan must be visible/loggable, since "task planning and decomposition" is directly graded.
- Maintains a shared state object (`user_profile`, `matched_schemes`, `chosen_scheme`, `form_data`, `status`) passed between agents — this is the "memory and state tracking across steps" requirement.
- Wraps each agent call in a try/except with a retry (max 2 attempts) — this is the "error handling" requirement. On repeated failure, log it and degrade gracefully (e.g. skip to next scheme, don't crash).
- Every agent action (start, output, retry, clarification asked) is appended to an `action_log` list with a timestamp and a one-line reason — this becomes the "transparent action log" the PS explicitly asks for.

### 2.2 Frontend
- **Streamlit** single-page interface.
- Input: one free-text box for the high-level instruction (plus a language preference toggle).
- Live-updating **Action Log panel** — the most important UI element for this PS; show each agent's step as it happens ("Eligibility Agent: checking 14 schemes against your profile...").
- Displays: clarifying question (if triggered) → shortlist of schemes → explanation → mock filled form → status/follow-up.

### 2.3 Agents
| Agent | Input | Output | Error/Clarification Handling |
|---|---|---|---|
| Eligibility Agent | User profile fields (parsed or asked for) | Ranked list of matching scheme IDs + reason | Asks a clarifying question if state/category/income is missing or ambiguous — not otherwise |
| Explainer Agent | Scheme ID(s) + chosen language | Plain-language explanation of benefits/eligibility/docs | If LLM call fails, retries once, then falls back to raw scheme data from JSON |
| Form-Fill Agent | Scheme ID + user profile | Pre-filled mock form (key-value pairs) | If a required field is missing, flags it in the form rather than guessing |
| Follow-up Agent | Application record | Status message + next reminder date | Rule-based — no LLM call needed, so no failure path required |

### 2.4 LLM Layer
- **Groq API** (free tier) running an open model (e.g. Llama 3.3 70B).
- Single wrapper function `call_llm(prompt, system=None)` used by all agents.
- Wrapper includes basic retry logic — this is where "handles failures and retries" is technically implemented.

### 2.5 Data Layer
- `data/schemes.json` — curated list of ~15–20 real schemes, each with:
  ```json
  {
    "id": "pm-kisan",
    "name": "PM-KISAN",
    "category": "agriculture",
    "eligibility": { "occupation": "farmer", "land_holding_max_acres": 5 },
    "benefits": "\u20b96,000/year in 3 installments",
    "required_documents": ["Aadhaar", "Land record", "Bank account"]
  }
  ```

### 2.6 Document Vault (Encrypted Local Storage)
Optional module — user can ignore it entirely. Handles sensitive document uploads (Aadhaar, land records, etc.) with a single passphrase for the whole vault.

**Flow:**
1. User sets a passphrase once (first upload). A random `salt` is generated and stored alongside the vault (salt is not secret, but must persist).
2. Key is derived via PBKDF2 from the passphrase + salt → used to create a Fernet key.
3. On upload: user selects a document type from a **dropdown** (Aadhaar Card, PAN Card, Birth Certificate, Land Record, Bank Passbook, Income Certificate, Caste Certificate, Domicile Certificate) or picks **"Other"**, which reveals a **free-text label box**.
4. File bytes are encrypted with the derived key and saved to `secure_storage/<label>.enc`, alongside a small unencrypted index file (`vault_index.json`) mapping labels → filenames only (no content).
5. When the Form-Fill Agent needs to check required documents for a scheme, it checks `vault_index.json` for matching labels — no decryption needed just to check presence.
6. Only when a document's actual content is needed is it decrypted, used in memory, and discarded — never written back to disk as plaintext.
7. Wrong passphrase → decryption fails cleanly (Fernet raises `InvalidToken`) → treated as a recoverable error (ask user to re-enter passphrase), not a crash.

**Files added:**
```
vault/
├── crypto_utils.py     # derive_key(), encrypt_file(), decrypt_file()
├── vault_index.json    # label -> encrypted filename mapping (no content)
└── secure_storage/      # encrypted files live here, e.g. aadhaar_card.enc
```

**Library:** Python's `cryptography` package (Fernet + PBKDF2HMAC) — free, open-source, well-audited. Do not hand-roll encryption.

**Explicitly never done:** documents are never sent to Groq, never logged in plaintext, never uploaded to any external service — the vault is 100% local to the machine running the demo.

## 3. Folder Structure
```
schemesaathi/
├── app.py                 # Streamlit entrypoint (instruction input + action log UI)
├── orchestrator.py         # LangGraph/CrewAI graph: planning, state, retries, action log
├── agents/
│   ├── eligibility_agent.py
│   ├── explainer_agent.py
│   ├── form_fill_agent.py
│   └── followup_agent.py
├── llm.py                  # Groq API wrapper with retry logic
├── data/
│   └── schemes.json
├── vault/
│   ├── crypto_utils.py
│   ├── vault_index.json
│   └── secure_storage/
└── requirements.txt
```

## 4. Tech Stack (all free)
- Orchestration: LangGraph / CrewAI
- LLM: Groq API (free tier)
- Frontend: Streamlit
- Data: JSON file
- Language output: prompted directly in target language, no separate translation service

## 5. What Makes This Genuinely "Agentic" (not just a pipeline)
- The orchestrator decides the plan dynamically, not a hardcoded sequence — if a scheme has no matching data, it should still adapt gracefully rather than fail the whole run.
- Clarification is conditional, not scripted — the agent should only ask when a required field is actually missing/ambiguous.
- The action log is a first-class UI element, not a debug console — it's how you visibly prove "task planning, orchestration, memory, and transparency" to judges in real time.

## 6. Future / Post-Hackathon Scaling (not built today)
- Replace flat JSON with a real scheme database, expandable via state e-governance partnerships.
- Aadhaar/DigiLocker integration for true auto-fill and identity verification.
- Deployment via Common Service Centres (CSCs) and NGOs for last-mile reach.
