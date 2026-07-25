# 🔍 SchemeSaathi — Full Codebase Audit Report

**Date:** 2026-07-25 | **Audited By:** Automated Deep Audit (User + Tester + QA POV)

---

## Audit Scope

Every source file, data file, and configuration in the project was reviewed line-by-line:

| Layer | Files Audited |
|---|---|
| **Core** | `llm.py`, `orchestrator.py`, `app.py` |
| **Agents** | `eligibility_agent.py`, `explainer_agent.py`, `form_fill_agent.py`, `followup_agent.py`, `profile_manager.py` |
| **Vault** | `crypto_utils.py`, `vault_manager.py` |
| **Data** | `schemes.json` (14 schemes) |
| **Config** | `.gitignore`, `.env`, `requirements.txt` |

---

## Bugs Found and Fixed

### 🔴 BUG #1 — Critical: Form Edit Key Mismatch (FIXED)

**File:** `app.py` (Lines 357-375)

**Problem:** When a user edited a form field (e.g., "Applicant Full Name") and clicked Save, the value was stored under the *form field key* (`applicant_name`) instead of the *profile key* (`name`). This meant the form-fill agent couldn't map it back on re-fill, so edits appeared to vanish.

**Root Cause:** The form field key in `GENERIC_FORM_FIELDS` is `applicant_name`, but the profile key is `name`. The save logic was doing `current_prof[form_key] = v` instead of `current_prof[profile_key] = v`.

**Fix:** Added a reverse mapping lookup (`field_to_profile_key`) that translates each form field key to its correct profile key before saving.

```diff
- for k, v in edited_form_values.items():
-     if v and v.strip():
-         current_prof[k] = v.strip()
+ for form_key, v in edited_form_values.items():
+     if v and v.strip():
+         profile_key = field_to_profile_key.get(form_key, form_key)
+         current_prof[profile_key] = v.strip()
```

---

### 🟡 BUG #2 — Reliability: External Image URL Dependency (FIXED)

**File:** `app.py` (Lines 78-79)

**Problem:** Sidebar loaded an image from `https://img.icons8.com/color/96/handshake.png`. If the demo environment has no internet (common at offline hackathon venues), Streamlit would show a broken image or throw an error.

**Fix:** Replaced with a local emoji-based markdown header.

---

## Verification Tests Passed

### Unit Test Suites (5/5 Passing)

| Test Suite | Status | Edge Cases Verified |
|---|---|---|
| `test_eligibility.py` | ✅ PASS | Complete profile, missing fields, NLP parsing, clarification triggers |
| `test_explainer.py` | ✅ PASS | English, Hindi (Devanagari), LLM fallback |
| `test_form_fill.py` | ✅ PASS | Full auto-fill, partial fill, persistent profile load |
| `test_followup.py` | ✅ PASS | ID generation, stage progression, reminder dates |
| `test_vault.py` | ✅ PASS | AES-256 encrypt/decrypt, wrong passphrase rejection, index matching |

### Edge Case Bug Hunt (17/17 Passing)

| Test | Input | Result |
|---|---|---|
| None input to eligibility | `None` | ✅ Triggers clarification |
| Empty string input | `""` | ✅ Triggers clarification |
| Empty dict input | `{}` | ✅ Triggers clarification |
| String-typed numbers | `{"age": "35", "income_lpa": "1.5"}` | ✅ Sanitized correctly |
| Negative age/income | `{"age": -5, "income_lpa": -1.0}` | ✅ No crash |
| Non-dict to sanitize | `"not a dict"` | ✅ Returns `{}` |
| Non-existent scheme ID | `"fake-scheme-xyz"` | ✅ Returns success=False |
| Empty scheme ID | `""` | ✅ Returns success=False |
| Empty shortlist | `[]` | ✅ Returns fallback message |
| Form-fill fake scheme | `"fake-scheme"` | ✅ Returns 0% completion |
| Form-fill None profile | `None` | ✅ Falls back to saved profile |
| Extra unknown keys | `{"random_key": "xyz"}` | ✅ Ignored gracefully |
| Bad stage override (99) | `stage_override=99` | ✅ Falls back to stage 2 |
| Malformed app ID | `"BADID"` | ✅ Extracts partial code |
| Empty doc list | `[]` | ✅ Returns all_present=True |
| Empty label upload | `""` | ✅ Raises ValueError |
| Orchestrator with {} | `user_input={}` | ✅ Triggers clarification |

### Data Integrity (14/14 Schemes Valid)

- ✅ 14 unique scheme IDs — no duplicates
- ✅ All required keys present (id, name, category, eligibility, benefits, required_documents, official_portal)
- ✅ All eligibility sub-keys present (occupation, max_income_lpa, gender, state)

### Security and Privacy Check

- ✅ `.env` file excluded from git
- ✅ `vault/vault_salt.bin` excluded from git
- ✅ `vault/secure_storage/*` excluded from git
- ✅ `vault/vault_index.json` excluded from git
- ✅ `data/user_profile.json` excluded from git
- ✅ No sensitive files in git tracked list (verified via `git ls-files`)

### Syntax Compilation

- ✅ All 10 Python source files compile without errors (py_compile)

---

## Remaining Issues

**None.** The codebase is clean, all bugs have been fixed, and all tests pass.
