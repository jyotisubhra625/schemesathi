import os
import json
from typing import Dict, Any, List, Optional
from agents.profile_manager import load_user_profile
from agents.explainer_agent import get_scheme_by_id

# Common scheme application form field templates
GENERIC_FORM_FIELDS = {
    "applicant_name": {"label": "Applicant Full Name", "profile_key": "name", "required": True},
    "age": {"label": "Age", "profile_key": "age", "required": True},
    "gender": {"label": "Gender", "profile_key": "gender", "required": True},
    "state": {"label": "State of Residence", "profile_key": "state", "required": True},
    "occupation": {"label": "Primary Occupation", "profile_key": "occupation", "required": True},
    "income_lpa": {"label": "Annual Family Income (in Lakhs)", "profile_key": "income_lpa", "required": True},
    "caste_category": {"label": "Caste Category", "profile_key": "caste_category", "required": False},
    "aadhaar_number": {"label": "Aadhaar Card Number", "profile_key": "aadhaar_number", "required": True},
    "bank_account_number": {"label": "Bank Account Number", "profile_key": "bank_account_number", "required": True},
    "bank_ifsc": {"label": "Bank IFSC Code", "profile_key": "bank_ifsc", "required": True}
}

SCHEME_SPECIFIC_FIELDS = {
    "pm-kisan": {
        "land_holding_acres": {"label": "Cultivable Land Holding (in Acres)", "profile_key": "land_holding_acres", "required": True},
        "khata_khatian_no": {"label": "Land Record / Khata Number", "profile_key": "khata_khatian_no", "required": True}
    },
    "ayushman-bharat": {
        "ration_card_number": {"label": "Ration Card / BPL Card Number", "profile_key": "ration_card_number", "required": True}
    },
    "pmay-g": {
        "housing_status": {"label": "Current Housing Status (Kutcha/Dilapidated)", "profile_key": "housing_status", "required": True},
        "job_card_mgnrega": {"label": "MGNREGA Job Card Number", "profile_key": "job_card_mgnrega", "required": False}
    },
    "pmegp": {
        "qualification": {"label": "Educational Qualification", "profile_key": "qualification", "required": True},
        "project_cost": {"label": "Proposed Project Cost (in ₹)", "profile_key": "project_cost", "required": True}
    },
    "subhadra-yojana": {
        "domicile_certificate_no": {"label": "Odisha Domicile Certificate No.", "profile_key": "domicile_certificate_no", "required": True}
    },
    "post-matric-scholarship": {
        "institution_name": {"label": "Current Institution / College Name", "profile_key": "institution_name", "required": True},
        "marksheet_percentage": {"label": "Previous Year Marksheet (%)", "profile_key": "marksheet_percentage", "required": True}
    }
}

def fill_form(
    scheme_id: str,
    user_profile: Optional[Dict[str, Any]] = None,
    schemes_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Form-Fill Agent: Auto-fills scheme application forms using user profile state.
    Flags missing fields and calculates form completion percentage.
    """
    if user_profile is None:
        user_profile = load_user_profile() or {}

    scheme = get_scheme_by_id(scheme_id, schemes_path)
    scheme_name = scheme["name"] if scheme else scheme_id.upper()

    # Combine generic form fields + scheme-specific fields
    fields_template = dict(GENERIC_FORM_FIELDS)
    if scheme_id in SCHEME_SPECIFIC_FIELDS:
        fields_template.update(SCHEME_SPECIFIC_FIELDS[scheme_id])

    filled_fields = {}
    missing_fields = []
    total_required = 0
    filled_required = 0

    for field_key, meta in fields_template.items():
        val = user_profile.get(meta["profile_key"])
        is_req = meta["required"]

        if is_req:
            total_required += 1

        if val is not None and str(val).strip() != "":
            filled_fields[field_key] = {
                "label": meta["label"],
                "value": val,
                "status": "Auto-filled"
            }
            if is_req:
                filled_required += 1
        else:
            filled_fields[field_key] = {
                "label": meta["label"],
                "value": "[MISSING - Action Needed]",
                "status": "Missing"
            }
            if is_req:
                missing_fields.append({
                    "field_key": field_key,
                    "label": meta["label"],
                    "required": True
                })

    completion_pct = round((filled_required / total_required * 100), 1) if total_required > 0 else 100.0
    ready_for_sub = len(missing_fields) == 0

    return {
        "scheme_id": scheme_id,
        "scheme_name": scheme_name,
        "filled_fields": filled_fields,
        "missing_fields": missing_fields,
        "completion_percentage": completion_pct,
        "ready_for_submission": ready_for_sub,
        "required_documents": scheme.get("required_documents", []) if scheme else []
    }

if __name__ == "__main__":
    test_prof = {
        "name": "Ramesh Kumar",
        "age": 38,
        "gender": "male",
        "state": "Odisha",
        "occupation": "farmer",
        "income_lpa": 1.5,
        "land_holding_acres": 2.5,
        "aadhaar_number": "XXXX-XXXX-1234",
        "bank_account_number": "98765432101",
        "bank_ifsc": "SBIN0001234"
    }

    result = fill_form("pm-kisan", user_profile=test_prof)
    print(f"Scheme: {result['scheme_name']}")
    print(f"Completion: {result['completion_percentage']}%")
    print(f"Ready for Submission: {result['ready_for_submission']}")
    print(f"Missing Fields: {len(result['missing_fields'])}")
