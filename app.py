import streamlit as st
import os
import json
from typing import Dict, Any

from agents.profile_manager import save_user_profile, load_user_profile, clear_user_profile
from vault.vault_manager import (
    upload_document,
    get_uploaded_document_labels,
    check_scheme_documents,
    STANDARD_DOCUMENT_DROPDOWN
)
from orchestrator import run_orchestrator_pipeline

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="SchemeSaathi — Autonomous Agentic Assistant",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Deep Teal & Mint Theme
st.markdown("""
    <style>
    .main-header {
        color: #0B3D3F;
        font-family: 'Segoe UI', serif;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #028090;
        font-size: 1.15rem;
        margin-bottom: 20px;
    }
    .action-card {
        background-color: #F4F9F8;
        border-left: 5px solid #028090;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 4px;
    }
    .status-plan { color: #0077B6; font-weight: bold; }
    .status-running { color: #E0A96D; font-weight: bold; }
    .status-success { color: #2A9D8F; font-weight: bold; }
    .status-clarification { color: #E76F51; font-weight: bold; }
    .status-error { color: #D62828; font-weight: bold; }
    
    .agent-badge {
        background-color: #0B3D3F;
        color: #FFFFFF;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Initialize Session State
# ---------------------------------------------------------
if "orchestrator_state" not in st.session_state:
    st.session_state.orchestrator_state = None

if "user_profile" not in st.session_state:
    st.session_state.user_profile = load_user_profile()

if "vault_passphrase" not in st.session_state:
    st.session_state.vault_passphrase = "mySecretVaultPassword"

# ---------------------------------------------------------
# Sidebar: Settings, Profile & Document Vault
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/handshake.png", width=64)
    st.title("SchemeSaathi Control")

    language = st.selectbox("🌐 Output Language / भाषा", ["English", "Hindi"], index=0)

    st.markdown("---")
    st.subheader("👤 User Profile Manager")
    
    prof = st.session_state.user_profile or {}
    with st.expander("Edit / Pre-fill Profile", expanded=False):
        name = st.text_input("Full Name", value=prof.get("name", ""), placeholder="e.g. Ramesh Kumar")
        
        age_val = prof.get("age")
        age = st.number_input("Age", min_value=1, max_value=110, value=int(age_val) if age_val else 25)
        
        gender_val = str(prof.get("gender") or "male").lower()
        gender = st.selectbox("Gender", ["male", "female", "other"], index=0 if gender_val=="male" else (1 if gender_val=="female" else 2))
        
        state_val = prof.get("state", "Odisha")
        states_list = ["Odisha", "Bihar", "Uttar Pradesh", "Maharashtra", "Other"]
        state_idx = states_list.index(state_val) if state_val in states_list else 0
        state_name = st.selectbox("State", states_list, index=state_idx)
        
        occ_val = str(prof.get("occupation") or "farmer").lower()
        occ_list = ["farmer", "student", "artisan", "street vendor", "self-employed", "homemaker", "unemployed", "None"]
        occ_idx = occ_list.index(occ_val) if occ_val in occ_list else 0
        occupation = st.selectbox("Occupation", occ_list, index=occ_idx)
        
        income_val = prof.get("income_lpa")
        income_lpa = st.number_input("Annual Income (LPA)", min_value=0.0, max_value=50.0, value=float(income_val) if income_val is not None else 1.5)
        
        caste_val = str(prof.get("caste_category") or "OBC").upper()
        caste_list = ["GENERAL", "OBC", "SC", "ST"]
        caste_idx = caste_list.index(caste_val) if caste_val in caste_list else 1
        caste = st.selectbox("Caste Category", ["General", "OBC", "SC", "ST"], index=caste_idx)
        
        aadhaar = st.text_input("Aadhaar Number", value=prof.get("aadhaar_number", ""), placeholder="e.g. 1234-5678-9012")
        bank_acc = st.text_input("Bank Account No.", value=prof.get("bank_account_number", ""), placeholder="e.g. 112233445566")
        bank_ifsc = st.text_input("Bank IFSC", value=prof.get("bank_ifsc", ""), placeholder="e.g. SBIN000456")

        if st.button("Save Profile"):
            updated_profile = {
                "name": name if name else "Citizen",
                "age": age,
                "gender": gender,
                "state": state_name,
                "occupation": None if occupation == "None" else occupation,
                "income_lpa": income_lpa,
                "caste_category": caste,
                "aadhaar_number": aadhaar,
                "bank_account_number": bank_acc,
                "bank_ifsc": bank_ifsc
            }
            st.session_state.user_profile = updated_profile
            save_user_profile(updated_profile)
            st.success("Profile updated successfully!")

        if st.button("Clear Profile"):
            clear_user_profile()
            st.session_state.user_profile = {}
            st.session_state.orchestrator_state = None
            st.rerun()

    st.markdown("---")
    st.subheader("🔒 Encrypted Document Vault")
    
    passphrase_input = st.text_input("Vault Passphrase", value=st.session_state.vault_passphrase, type="password")
    st.session_state.vault_passphrase = passphrase_input

    with st.expander("Upload & Encrypt Document", expanded=False):
        uploaded_file = st.file_uploader("Choose document file", type=["pdf", "png", "jpg", "txt", "bin"])
        doc_label = st.selectbox("Document Label", STANDARD_DOCUMENT_DROPDOWN)
        custom_label = None
        if doc_label == "Other":
            custom_label = st.text_input("Custom Label")

        if st.button("Upload to Vault"):
            if uploaded_file and passphrase_input:
                file_bytes = uploaded_file.read()
                try:
                    res = upload_document(
                        passphrase_input,
                        file_bytes,
                        doc_label,
                        custom_label=custom_label
                    )
                    st.success(f"Encrypted & saved: {res['label']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Vault Upload Error: {e}")
            else:
                st.warning("Please select a file and enter a passphrase.")

    # Show Vault Contents
    vault_labels = get_uploaded_document_labels()
    st.markdown(f"**Stored Vault Documents ({len(vault_labels)}):**")
    if vault_labels:
        for lbl in vault_labels:
            st.markdown(f"- 📁 `{lbl}` *(Encrypted)*")
    else:
        st.info("Vault is currently empty.")

# ---------------------------------------------------------
# Main App Header & Instruction Entry Point
# ---------------------------------------------------------
st.markdown("<h1 class='main-header'>🤝 SchemeSaathi</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Autonomous Agentic Personal Assistant for Government Welfare Schemes</div>", unsafe_allow_html=True)

instruction_input = st.text_area(
    "💬 Give SchemeSaathi your instruction:",
    value="Find out what government schemes I'm eligible for and get my applications ready.",
    height=80
)

col_run, col_clear = st.columns([1, 4])
with col_run:
    run_btn = st.button("🚀 Run Agentic Pipeline", type="primary", use_container_width=True)

if run_btn:
    with st.spinner("Agentic orchestrator planning & executing..."):
        state = run_orchestrator_pipeline(
            user_input=st.session_state.user_profile if st.session_state.user_profile else instruction_input,
            language=language
        )
        st.session_state.orchestrator_state = state

# ---------------------------------------------------------
# Handle Active Pipeline Execution State
# ---------------------------------------------------------
state = st.session_state.orchestrator_state

if state:
    st.markdown("---")
    
    # Check if Conditional Clarification is needed
    if state.get("needs_clarification"):
        st.warning("⚠️ **Clarification Required from User**")
        st.info(state["clarification_question"])
        
        missing = state.get("missing_fields", [])
        user_answers = {}
        for field in missing:
            if field == "occupation":
                user_answers[field] = st.selectbox(
                    "Select your occupation:",
                    ["farmer", "student", "artisan", "street vendor", "self-employed", "homemaker", "unemployed"]
                )
            elif field == "state":
                user_answers[field] = st.selectbox("Select your state:", ["Odisha", "Bihar", "Uttar Pradesh", "Maharashtra"])
            else:
                user_answers[field] = st.text_input(f"Enter {field}:")
        
        if st.button("Submit Clarification & Resume Agent", type="primary"):
            resumed_state = run_orchestrator_pipeline(
                user_input=state["user_profile"],
                language=language,
                existing_state=state,
                clarification_response=user_answers
            )
            st.session_state.orchestrator_state = resumed_state
            st.rerun()

    # Layout: Two Columns (Left: Action Log, Right: Results)
    col_log, col_res = st.columns([1, 1])

    # -----------------------------------------------------
    # Left Column: Transparent Action Log
    # -----------------------------------------------------
    with col_log:
        st.subheader("📋 Transparent Action Log")
        st.caption("Real-time decision trace & agent decomposition (PS1 Requirement)")
        
        # Display Execution Sub-task Plan Progress
        with st.expander("📌 Orchestrator Execution Plan", expanded=True):
            for task in state.get("plan", []):
                status_icon = "🟢" if task["status"]=="completed" else ("🟡" if task["status"]=="in_progress" else "⚪")
                st.markdown(f"{status_icon} **Step {task['step_id']}: {task['title']}** — `{task['agent']}`")

        # Action Log Timeline
        st.markdown("#### Execution Activity Stream")
        for log in reversed(state.get("action_log", [])):
            status_class = f"status-{log['status'].lower()}"
            st.markdown(f"""
                <div class='action-card'>
                    <span class='agent-badge'>{log['agent']}</span>
                    <span style='float: right; font-size: 0.8rem; color: #666;'>{log['timestamp']}</span><br/>
                    <strong>{log['action']}</strong> — <span class='{status_class}'>[{log['status']}]</span><br/>
                    <small>{log['reasoning']}</small>
                </div>
            """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # Right Column: Results, Explanations, Forms & Tracking
    # -----------------------------------------------------
    with col_res:
        st.subheader("🎯 Scheme Results & Applications")

        tab_schemes, tab_explain, tab_form, tab_track = st.tabs([
            "Shortlisted Schemes",
            "Scheme Explanation",
            "Form Preview & Vault",
            "Application Status"
        ])

        # Tab 1: Matched Schemes
        with tab_schemes:
            matched = state.get("matched_schemes", [])
            if matched:
                st.success(f"Matched {len(matched)} Eligible Scheme(s)")
                chosen_id = state.get("chosen_scheme_id")
                for idx, scheme in enumerate(matched):
                    with st.container():
                        is_selected = (scheme['id'] == chosen_id)
                        header_badge = " [SELECTED FOR APPLICATION]" if is_selected else ""
                        st.markdown(f"### {idx+1}. {scheme['name']} ⭐ ({scheme['score']} pts){header_badge}")
                        st.markdown(f"**Category:** `{scheme.get('category', 'general').upper()}`")
                        st.markdown(f"**Benefits:** {scheme.get('benefits')}")
                        reasons_list = scheme.get("reasons", [])
                        why_matched = ", ".join(reasons_list) if reasons_list else "Matches user profile eligibility criteria"
                        st.markdown(f"**Why Matched:** {why_matched}")
                        
                        if not is_selected:
                            if st.button(f"👉 Select & Prepare Application Form for {scheme['id'].upper()}", key=f"btn_select_{scheme['id']}"):
                                updated_state = run_orchestrator_pipeline(
                                    user_input=st.session_state.user_profile if st.session_state.user_profile else instruction_input,
                                    language=language,
                                    chosen_scheme_id=scheme['id']
                                )
                                st.session_state.orchestrator_state = updated_state
                                st.rerun()
                        else:
                            st.info("✅ Currently selected scheme. View form and document checks in the 'Form Preview & Vault' tab.")
                        st.markdown("---")
            else:
                st.info("No matching schemes found for current profile.")

        # Tab 2: Multilingual Explanation
        with tab_explain:
            expl = state.get("explanation")
            if expl:
                st.markdown(f"### Explanation ({expl.get('language', language)})")
                st.write(expl.get("explanation"))
            else:
                st.info("Run the agent pipeline to generate a scheme explanation.")

        # Tab 3: Form Preview & Vault Verification
        with tab_form:
            form = state.get("filled_form")
            vault_info = state.get("vault_status")

            if form:
                st.markdown(f"### Application Form: `{form.get('scheme_name')}`")
                st.progress(form.get("completion_percentage", 0.0) / 100.0)
                st.markdown(f"**Completion Status:** `{form.get('completion_percentage')}%` | **Ready for Submission:** `{form.get('ready_for_submission')}`")
                
                st.markdown("#### ✏️ Interactive Application Form Preview")
                st.caption("All fields below are auto-filled from your profile and vault. You can edit any field directly below.")
                
                filled = form.get("filled_fields", {})
                edited_form_values = {}

                col_f1, col_f2 = st.columns(2)
                field_items = list(filled.items())

                for idx, (f_key, meta) in enumerate(field_items):
                    col = col_f1 if idx % 2 == 0 else col_f2
                    with col:
                        lbl = meta.get("label", f_key)
                        raw_val = meta.get("value", "")
                        display_val = "" if str(raw_val).startswith("[MISSING") else str(raw_val)
                        
                        edited_form_values[f_key] = st.text_input(
                            f"{lbl}",
                            value=display_val,
                            key=f"form_edit_{form.get('scheme_id')}_{f_key}",
                            placeholder=f"Enter {lbl}..."
                        )

                if st.button("💾 Save Form Edits & Update Profile", type="secondary", use_container_width=True):
                    current_prof = st.session_state.user_profile or {}
                    for k, v in edited_form_values.items():
                        if v and v.strip():
                            current_prof[k] = v.strip()
                    
                    st.session_state.user_profile = current_prof
                    save_user_profile(current_prof)

                    # Re-run form-fill for updated profile
                    refilled = fill_form(form["scheme_id"], current_prof)
                    state["filled_form"] = refilled
                    st.session_state.orchestrator_state = state
                    st.success("Application form edits saved successfully!")
                    st.rerun()

                if vault_info:
                    st.markdown("#### 🔒 Encrypted Vault Document Verification")
                    pres = vault_info.get("present_documents", [])
                    miss = vault_info.get("missing_documents", [])

                    for p in pres:
                        st.markdown(f"✅ **{p['required']}** — *Found in Vault (`{p['found_label']}`)*")
                    for m in miss:
                        st.markdown(f"⚠️ **{m}** — *Missing from Vault (Please Upload in Sidebar)*")

                st.markdown("---")
                st.markdown("#### 👤 Human-in-the-Loop Review & Submission Control")
                if state.get("user_confirmed_submission"):
                    st.success("✅ **Application Approved & Registered by Citizen!** Tracking record active in 'Application Status' tab.")
                else:
                    st.info("Please review the pre-filled form fields and document checks above. Once verified, confirm submission below:")
                    if st.button("✅ Review Complete — Confirm & Register Application", type="primary", use_container_width=True):
                        from agents.followup_agent import create_application_record
                        scheme_id = form.get("scheme_id", "scheme")
                        applicant_name = (st.session_state.user_profile or {}).get("name", "Citizen")
                        app_record = create_application_record(scheme_id, applicant_name=applicant_name)
                        
                        state["user_confirmed_submission"] = True
                        state["application_record"] = app_record
                        st.session_state.orchestrator_state = state
                        st.success("🎉 Application Submitted Successfully! View status in the 'Application Status' tab.")
                        st.rerun()
            else:
                st.info("Form auto-fill data will appear here after execution.")

        # Tab 4: Application Tracking & Status
        with tab_track:
            app_rec = state.get("application_record")
            if app_rec:
                st.markdown(f"### Application Tracker: `{app_rec.get('application_id')}`")
                st.markdown(f"**Scheme:** {app_rec.get('scheme_name')}")
                st.markdown(f"**Current Status:** `{app_rec.get('current_status') or app_rec.get('status_title')}`")
                
                st.markdown("#### Application Progression Timeline")
                timeline = app_rec.get("timeline", [])
                if not timeline and "stages_timeline" in app_rec:
                    cur_stage = app_rec.get("current_stage", 1)
                    timeline = [
                        {
                            "stage": s["stage"],
                            "name": s["name"],
                            "status": "Completed" if s["stage"] < cur_stage else ("In Progress" if s["stage"] == cur_stage else "Pending")
                        }
                        for s in app_rec["stages_timeline"]
                    ]

                for stage in timeline:
                    icon = "✅" if stage["status"]=="Completed" else ("🔄" if stage["status"]=="In Progress" else "⏳")
                    st.markdown(f"{icon} **Stage {stage['stage']}: {stage['name']}** — `{stage['status']}`")
                
                next_act = app_rec.get("next_action") or f"Check for application updates on or before {app_rec.get('next_reminder_date')}."
                st.info(f"💡 **Next Action / Reminder:** {next_act}")
            else:
                st.info("Application status tracking record will be generated after running the pipeline.")
