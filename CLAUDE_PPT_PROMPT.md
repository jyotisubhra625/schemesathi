# 🎯 OFFICIAL 6-7 SLIDE HACKATHON MASTER PPT PROMPT

Copy and paste the prompt below into **Claude.ai**, **ChatGPT**, or **Gamma.app** to generate a presentation deck that matches the official submission guidelines!

---

### 📋 COPY THE PROMPT BELOW:

```text
You are an elite AI hackathon pitch designer. Create a complete, highly persuasive, professional 6-to-7 slide presentation deck for a winning hackathon submission named "SchemeSaathi".

### OFFICIAL SUBMISSION CONTEXT:
- Project Name: SchemeSaathi (🤝 Autonomous Agentic Personal Assistant for Government Welfare Schemes)
- Track / Problem Statement: Problem Statement 1 — Agentic AI for Citizen Welfare Services
- GitHub Repository: https://github.com/jyotisubhra625/schemesathi
- Tech Stack: Python 3.11, Streamlit, LangGraph Multi-Agent Orchestrator, Cryptography (PBKDF2 + AES-256 Fernet), ReportLab (PDF Engine), gTTS (Text-to-Speech), Requests HTTP.

---

### SLIDE-BY-SLIDE CONTENT REQUIREMENTS (EXACTLY 6-7 SLIDES):

Please generate detailed content formatted clearly with:
- Slide Title
- Visual/Layout Suggestions (e.g. 2-Column, 3-Card Grid, Architecture Flowchart)
- Bullet Points (Key Talk Track)
- Highlight Box / Key Takeaway

#### SLIDE 1: Title, Team & Executive Summary
- Project Title: SchemeSaathi
- Subtitle: Autonomous Agentic Personal Assistant for Government Welfare Schemes
- Team Information Placeholder Box:
  1. Team Name: FrankByte
  2. Team Leader's Name: Subhrajyoti Das
  3. Team Members: Aritra Nath , Sushmita Chakraborty
  4. Selected Track: Problem Statement 1 — Agentic AI for Citizen Welfare Services
- Tagline: Empowering 1.4 Billion Citizens with Zero-Barrier Access to Welfare Benefits via Agentic AI & Secure Encrypted Vaults.

#### SLIDE 2: The Problem — India's Welfare Access Gap
- Information Asymmetry: 500+ Central and State welfare schemes exist, but citizens lack awareness of complex eligibility rules.
- Document Bureaucracy: Over 40% of applications are rejected due to missing or mismatched documents (Aadhaar, Land records, Bank Passbooks).
- Language & Digital Divide: Official portals are text-heavy and English/Hindi centric, excluding rural and low-literacy beneficiaries.
- Operational Bottleneck: Citizens spend days visiting Gram Panchayat or CSC centers for basic eligibility checks.

#### SLIDE 3: The Solution & Multi-Agent Architecture
- Multi-Agent Orchestrator (LangGraph / Plan-and-Execute): Automatically plans, matches eligibility, checks documents, pre-fills forms, and tracks applications.
- System Flow: Citizen Input -> ProfileAgent -> SchemeAPI Client (HTTP) -> EligibilityAgent -> VaultAgent (AES-256) -> FormFillAgent -> ExplainerAgent (gTTS Audio) -> FollowUpAgent (.ics)
- Sub-Agents Breakdown:
  1. ProfileAgent: Extracts citizen demographics.
  2. SchemeAPI Client: Connects live to HTTP endpoints (api.myscheme.gov.in) with cached fallback.
  3. EligibilityAgent: Evaluates policy rules across 16+ Central & State schemes.
  4. FormFillAgent: Auto-fills 100% of application fields with profile data.
  5. ExplainerAgent: Generates multilingual explanations + MP3 speech audio.

#### SLIDE 4: Zero-Trust Security & Encrypted Vault Privacy Design
- Master PIN Protection: Documents (Aadhaar, Land records) are encrypted on disk using PBKDF2 key derivation (100k iterations + SHA256) + AES-256 Fernet encryption. Plaintext never touches disk.
- Zero-Knowledge Metadata Index: Agent verifies document presence using metadata headers without decrypting private document contents until PIN authorization.
- Human-in-the-Loop Review: Citizens retain full control to inspect, edit, and confirm pre-filled form fields before final submission.

#### SLIDE 5: Production-Grade Features & Differentiators
- Feature 1: 📄 Official PDF Form Exporter (ReportLab) — Generates print-ready, official Indian Government Welfare Application PDFs with reference IDs and signature blocks.
- Feature 2: 🔊 Multilingual Voice Audio Guide (gTTS) — Converts scheme explanations into natural Hindi & English speech audio for low-literacy citizens.
- Feature 3: 🏛️ Central vs State Jurisdiction Filter — Instant radio filtering across Central and regional State Government schemes (e.g. Subhadra Yojana, KALIA Scheme, Ladli Behna).
- Feature 4: 📅 iCalendar (.ics) Reminders Exporter — Exports standard RFC 5545 calendar events directly to Google Calendar, Apple Calendar, or Outlook for stage verification deadlines.
- Feature 5: 📊 Household Financial Benefit Analytics — Metric cards calculating total annual monetary grants (e.g. ₹18,000/yr) and healthcare insurance coverage (₹5.0 Lakhs).

#### SLIDE 6: Real-World Social Impact, Scalability & Tech Stack
- Social Impact: Bridges the digital divide for rural India, empowering farmers, artisans, women, students, senior citizens, and street vendors.
- Technical Scalability: Easily extensible to 500+ Central and State schemes by connecting to official government APIs.
- Tech Stack: Python 3.11, Streamlit, LangGraph, Cryptography (Fernet/PBKDF2), ReportLab, gTTS, Requests HTTP.

#### SLIDE 7: Live Demo & Official Submission Links
- Deployed Application URL: [Insert Your Deployed Streamlit URL]
- GitHub Repository: https://github.com/jyotisubhra625/schemesathi
- Google Drive Links Check: Public Viewing Access Enabled ("Anyone with the link can view")
- Final Q&A Readiness & Thank You
```
