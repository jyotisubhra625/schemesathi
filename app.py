import streamlit as st
import os
import json
from typing import Dict, Any
# Fresh reload: 2026-07-25

from agents.profile_manager import save_user_profile, load_user_profile, clear_user_profile
from vault.vault_manager import (
    upload_document,
    get_uploaded_document_labels,
    check_scheme_documents,
    read_decrypted_document,
    delete_document,
    verify_vault_passphrase,
    STANDARD_DOCUMENT_DROPDOWN
)
from orchestrator import run_orchestrator_pipeline

# ---------------------------------------------------------
# Global Constants
# ---------------------------------------------------------
INDIAN_STATES_AND_UTS = [
    "Odisha",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
    "Other"
]

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

if "vault_unlocked" not in st.session_state:
    st.session_state.vault_unlocked = False

if "vault_passphrase" not in st.session_state:
    st.session_state.vault_passphrase = ""

if "preview_doc_label" not in st.session_state:
    st.session_state.preview_doc_label = None

# ---------------------------------------------------------
# Sidebar: Settings, Profile & Document Vault
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 🤝 SchemeSaathi Control")

    language = st.selectbox("🌐 Output Language / भाषा", ["English", "Hindi"], index=0)

    st.markdown("---")
    st.subheader("👤 User Profile Manager")
    
    prof = st.session_state.user_profile or {}
    with st.expander("Edit / Pre-fill Profile", expanded=False):
        name = st.text_input("Full Name", value=prof.get("name", ""), placeholder="e.g. Ramesh Kumar")
        
        age_raw = prof.get("age")
        try:
            parsed_age = int(age_raw) if age_raw is not None else 25
            clean_age = max(1, min(110, parsed_age))
        except (ValueError, TypeError):
            clean_age = 25
        age = st.number_input("Age", min_value=1, max_value=110, value=clean_age)
        
        gender_val = str(prof.get("gender") or "male").lower()
        gender = st.selectbox("Gender", ["male", "female", "other"], index=0 if gender_val=="male" else (1 if gender_val=="female" else 2))
        
        state_val = prof.get("state", "Odisha")
        states_list = INDIAN_STATES_AND_UTS
        state_idx = states_list.index(state_val) if state_val in states_list else 0
        state_name = st.selectbox("State", states_list, index=state_idx)
        
        occ_val = str(prof.get("occupation") or "farmer").lower()
        occ_list = ["farmer", "student", "artisan", "street vendor", "self-employed", "homemaker", "unemployed", "None"]
        occ_idx = occ_list.index(occ_val) if occ_val in occ_list else 0
        occupation = st.selectbox("Occupation", occ_list, index=occ_idx)
        
        inc_raw = prof.get("income_lpa")
        try:
            parsed_inc = float(inc_raw) if inc_raw is not None else 1.5
            clean_inc = max(0.0, min(50.0, parsed_inc))
        except (ValueError, TypeError):
            clean_inc = 1.5
        income_lpa = st.number_input("Annual Income (LPA)", min_value=0.0, max_value=50.0, value=clean_inc)
        
        caste_val = str(prof.get("caste_category") or "OBC").upper()
        caste_list = ["GENERAL", "OBC", "SC", "ST"]
        caste_idx = caste_list.index(caste_val) if caste_val in caste_list else 1
        caste = st.selectbox("Caste Category", ["General", "OBC", "SC", "ST"], index=caste_idx)
        
        aadhaar = st.text_input("Aadhaar Number", value=prof.get("aadhaar_number", ""), placeholder="e.g. 1234-5678-9012")
        bank_acc = st.text_input("Bank Account No.", value=prof.get("bank_account_number", ""), placeholder="e.g. 112233445566")
        bank_ifsc = st.text_input("Bank IFSC", value=prof.get("bank_ifsc", ""), placeholder="e.g. SBIN000456")

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
        
        # Auto-sync live sidebar profile state
        st.session_state.user_profile = updated_profile
        save_user_profile(updated_profile)

        if st.button("Clear Profile"):
            clear_user_profile()
            st.session_state.user_profile = {}
            st.session_state.orchestrator_state = None
            st.rerun()

    st.markdown("---")
    st.subheader("🔐 Citizen Vault Setup & Login")
    
    has_stored_files = len(get_uploaded_document_labels()) > 0
    has_pin_set = bool(st.session_state.vault_passphrase)
    
    if not st.session_state.vault_unlocked:
        if not has_pin_set and not has_stored_files:
            # Mode A: First-time PIN setup
            st.info("🔑 **First-Time Vault Setup**: Create your secret Vault PIN to encrypt your documents with AES-256 protection.")
            pin_input = st.text_input("Create Secret Vault PIN", type="password", key="create_vault_pin", placeholder="e.g. 1234 or mysecretpass")
            pin_confirm = st.text_input("Confirm Vault PIN", type="password", key="confirm_vault_pin", placeholder="Re-enter PIN...")
            
            if st.button("💾 Set PIN & Unlock Vault", type="primary", use_container_width=True):
                if pin_input and pin_input.strip():
                    if pin_input == pin_confirm:
                        st.session_state.vault_passphrase = pin_input.strip()
                        st.session_state.vault_unlocked = True
                        st.success("🎉 Vault PIN set & Vault Unlocked!")
                        st.rerun()
                    else:
                        st.error("PINs do not match. Please re-enter.")
                else:
                    st.warning("Please enter a PIN.")
        else:
            # Mode B: PIN already established - Enter PIN to unlock
            st.info("🔒 **Vault Locked**: Enter your Secret PIN to access and decrypt your stored documents.")
            unlock_pin = st.text_input("Enter Secret Vault PIN", type="password", key="unlock_vault_pin", placeholder="Enter your PIN...")
            
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                if st.button("🔓 Unlock", type="primary", use_container_width=True):
                    if unlock_pin and unlock_pin.strip():
                        key = unlock_pin.strip()
                        if verify_vault_passphrase(key):
                            st.session_state.vault_passphrase = key
                            st.session_state.vault_unlocked = True
                            st.success("Vault Unlocked!")
                            st.rerun()
                        else:
                            st.error("Incorrect PIN. Could not decrypt vault files.")
                    else:
                        st.warning("Please enter your PIN.")
            with col_u2:
                if st.button("🔄 Reset PIN", use_container_width=True):
                    st.session_state.vault_passphrase = ""
                    st.session_state.vault_unlocked = False
                    st.rerun()
    else:
        st.success("🟢 **Vault Unlocked (AES-256 Active)**")
        st.caption("Master PIN Active. Uploads encrypted with PBKDF2 + AES-256 Fernet.")
        if st.button("🔒 Lock Vault Session", use_container_width=True):
            st.session_state.vault_unlocked = False
            st.session_state.preview_doc_label = None
            st.rerun()

        with st.expander("📤 Upload & Encrypt New Document", expanded=False):
            uploaded_file = st.file_uploader("Select document (PNG, JPG, PDF, TXT)", type=["pdf", "png", "jpg", "jpeg", "txt"])
            doc_label = st.selectbox("Document Category", STANDARD_DOCUMENT_DROPDOWN)
            custom_label = None
            if doc_label == "Other":
                custom_label = st.text_input("Custom Category Name")

            if st.button("🔒 Encrypt & Store in Vault", type="primary", use_container_width=True):
                if uploaded_file and st.session_state.vault_passphrase:
                    file_bytes = uploaded_file.read()
                    try:
                        res = upload_document(
                            st.session_state.vault_passphrase,
                            file_bytes,
                            doc_label,
                            custom_label=custom_label
                        )
                        st.success(f"Encrypted & saved: `{res['label']}`")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Vault Upload Error: {e}")
                else:
                    st.warning("Please select a file.")

        vault_labels = get_uploaded_document_labels()
        st.markdown(f"**Stored Encrypted Files ({len(vault_labels)}):**")
        if vault_labels:
            for lbl in vault_labels:
                col_sb1, col_sb2, col_sb3, col_sb4 = st.columns([3, 1, 1, 1])
                with col_sb1:
                    st.markdown(f"📁 `{lbl}`")
                with col_sb2:
                    if st.button("👁️", key=f"sb_prev_{lbl}", help=f"Preview {lbl}"):
                        st.session_state.preview_doc_label = lbl
                        st.rerun()
                with col_sb3:
                    try:
                        raw_bytes = read_decrypted_document(st.session_state.vault_passphrase, lbl)
                        st.download_button(
                            label="📥",
                            data=raw_bytes,
                            file_name=f"{lbl.lower().replace(' ', '_')}.bin",
                            mime="application/octet-stream",
                            key=f"sb_dl_{lbl}",
                            help=f"Download {lbl}"
                        )
                    except Exception:
                        st.caption("🔒")
                with col_sb4:
                    if st.button("🗑️", key=f"sb_del_{lbl}", help=f"Delete {lbl}"):
                        delete_document(lbl)
                        if st.session_state.preview_doc_label == lbl:
                            st.session_state.preview_doc_label = None
                        st.success(f"Deleted `{lbl}`")
                        st.rerun()

            # Sidebar Live File Preview Box
            active_prev = st.session_state.preview_doc_label
            if active_prev and active_prev in vault_labels:
                st.markdown("---")
                st.markdown(f"**👁️ Decrypted Preview: `{active_prev}`**")
                if st.button("❌ Close Preview", key="sb_btn_close_preview", type="secondary", use_container_width=True):
                    st.session_state.preview_doc_label = None
                    st.rerun()
                try:
                    dec_b = read_decrypted_document(st.session_state.vault_passphrase, active_prev)
                    if dec_b.startswith(b'\x89PNG') or dec_b.startswith(b'\xff\xd8') or dec_b.startswith(b'RIFF') or dec_b.startswith(b'GIF'):
                        st.image(dec_b, caption=active_prev, use_container_width=True)
                    else:
                        try:
                            txt = dec_b.decode("utf-8")
                            st.text_area("Content:", value=txt, height=120)
                        except Exception:
                            st.info(f"Binary file ({len(dec_b)} bytes). Click 📥 to download.")
                except Exception as e:
                    st.error(f"Decryption failed: {e}")
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
            user_input=instruction_input if (instruction_input and instruction_input.strip()) else st.session_state.user_profile,
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
        saved_p = st.session_state.user_profile or {}
        for field in missing:
            if field == "occupation":
                occ_curr = str(saved_p.get("occupation") or "farmer").lower()
                occ_opts = ["farmer", "student", "artisan", "street vendor", "self-employed", "homemaker", "unemployed"]
                occ_idx = occ_opts.index(occ_curr) if occ_curr in occ_opts else 0
                user_answers[field] = st.selectbox(
                    "Select your occupation:",
                    occ_opts,
                    index=occ_idx
                )
            elif field == "state":
                state_curr = saved_p.get("state", "Odisha")
                st_opts = INDIAN_STATES_AND_UTS
                st_idx = st_opts.index(state_curr) if state_curr in st_opts else 0
                user_answers[field] = st.selectbox("Select your state:", st_opts, index=st_idx)
            elif field == "income_lpa":
                inc_curr = saved_p.get("income_lpa")
                def_inc = str(inc_curr) if inc_curr is not None else "1.5"
                user_answers[field] = st.text_input("Enter Annual Income in Lakhs (income_lpa):", value=def_inc)
            else:
                default_val = str(saved_p.get(field) or "")
                user_answers[field] = st.text_input(f"Enter {field}:", value=default_val)
        
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
            form = state.get("filled_form") if state else None
            vault_info = state.get("vault_status") if state else None

            if form:
                st.markdown(f"### Application Form: `{form.get('scheme_name')}`")
                st.progress(form.get("completion_percentage", 0.0) / 100.0)
                st.markdown(f"**Completion Status:** `{form.get('completion_percentage')}%` | **Ready for Submission:** `{form.get('ready_for_submission')}`")
                
                st.markdown("#### ✏️ Interactive Application Form Preview")
                st.caption("All fields below are auto-filled from your profile and vault. You can edit any field directly below.")
                
                filled = form.get("filled_fields", {})
                edited_form_values = {}

                # Build reverse mapping: form_field_key -> profile_key
                from agents.form_fill_agent import GENERIC_FORM_FIELDS, SCHEME_SPECIFIC_FIELDS
                field_to_profile_key = {}
                for fk, meta in GENERIC_FORM_FIELDS.items():
                    field_to_profile_key[fk] = meta["profile_key"]
                scheme_specific = SCHEME_SPECIFIC_FIELDS.get(form.get("scheme_id"), {})
                for fk, meta in scheme_specific.items():
                    field_to_profile_key[fk] = meta["profile_key"]

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
                    for form_key, v in edited_form_values.items():
                        if v and v.strip():
                            profile_key = field_to_profile_key.get(form_key, form_key)
                            current_prof[profile_key] = v.strip()
                    
                    st.session_state.user_profile = current_prof
                    save_user_profile(current_prof)

                    # Re-run form-fill for updated profile
                    refilled = fill_form(form["scheme_id"], current_prof)
                    state["filled_form"] = refilled
                    st.session_state.orchestrator_state = state
                    st.success("Application form edits saved successfully!")
                    st.rerun()

                if vault_info:
                    st.markdown("---")
                    st.markdown("#### 🔒 Scheme Document Requirements Verification")
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
                st.info("💡 Run the Agentic Pipeline to view the auto-filled application form for your selected scheme.")

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
