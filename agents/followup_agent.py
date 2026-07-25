import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from agents.explainer_agent import get_scheme_by_id

APPLICATION_STAGES = [
    {"stage": 1, "name": "Application Submitted", "desc": "Application received and reference ID generated."},
    {"stage": 2, "name": "Document Verification", "desc": "Verification by Gram Panchayat / Urban Local Body officer."},
    {"stage": 3, "name": "District Sanction", "desc": "Approved by District Task Force / Nodal Officer."},
    {"stage": 4, "name": "Fund Disbursal (DBT)", "desc": "Direct Benefit Transfer initiated into linked bank account."}
]

def generate_application_id(scheme_id: str) -> str:
    """Generates a realistic government application reference number."""
    prefix = scheme_id.replace("-", "").upper()[:4]
    random_num = random.randint(10000, 99999)
    year = datetime.now().year
    return f"APP-{year}-{prefix}-{random_num}"

def create_application_record(
    scheme_id: str,
    applicant_name: str = "Citizen",
    schemes_path: Optional[str] = None
) -> Dict[str, Any]:
    """Creates a new tracked application record."""
    scheme = get_scheme_by_id(scheme_id, schemes_path)
    scheme_name = scheme["name"] if scheme else scheme_id.upper()
    app_id = generate_application_id(scheme_id)

    today = datetime.now()
    next_reminder = today + timedelta(days=7)
    est_completion = today + timedelta(days=21)

    return {
        "application_id": app_id,
        "scheme_id": scheme_id,
        "scheme_name": scheme_name,
        "applicant_name": applicant_name,
        "submitted_date": today.strftime("%Y-%m-%d"),
        "current_stage": 1,
        "current_status": APPLICATION_STAGES[0]["name"],
        "status_description": APPLICATION_STAGES[0]["desc"],
        "estimated_completion_date": est_completion.strftime("%Y-%m-%d"),
        "next_reminder_date": next_reminder.strftime("%Y-%m-%d"),
        "stages_timeline": APPLICATION_STAGES
    }

def track_application(
    application_id: str,
    stage_override: Optional[int] = None
) -> Dict[str, Any]:
    """
    Follow-up Agent: Returns tracking details, current status, and next reminder.
    """
    # Extract scheme code from application_id if format matches APP-YYYY-CODE-XXXXX
    parts = application_id.split("-")
    scheme_code = parts[2] if len(parts) >= 3 else "SCHEME"

    stage_idx = stage_override if stage_override and 1 <= stage_override <= 4 else 2
    current_stage_info = APPLICATION_STAGES[stage_idx - 1]

    today = datetime.now()
    reminder_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")

    return {
        "application_id": application_id,
        "scheme_id": scheme_code.lower(),
        "current_stage": stage_idx,
        "total_stages": 4,
        "status_title": current_stage_info["name"],
        "status_description": current_stage_info["desc"],
        "next_action": f"Check status update on or before {reminder_date}.",
        "next_reminder_date": reminder_date,
        "is_complete": stage_idx == 4,
        "timeline": [
            {
                "stage": s["stage"],
                "name": s["name"],
                "status": "Completed" if s["stage"] < stage_idx else ("In Progress" if s["stage"] == stage_idx else "Pending")
            }
            for s in APPLICATION_STAGES
        ]
    }

def get_demo_followup_summary(applicant_name: str = "Ramesh Kumar") -> List[Dict[str, Any]]:
    """Returns sample active applications dashboard for demo purposes."""
    app1 = create_application_record("pm-kisan", applicant_name=applicant_name)
    app2 = create_application_record("ayushman-bharat", applicant_name=applicant_name)
    app2["current_stage"] = 2
    app2["current_status"] = APPLICATION_STAGES[1]["name"]

    return [app1, app2]

if __name__ == "__main__":
    record = create_application_record("pm-kisan", applicant_name="Sita Devi")
    print(f"Created App ID: {record['application_id']}")
    print(f"Status: {record['current_status']}")

    tracking = track_application(record['application_id'], stage_override=2)
    print(f"Tracking Stage: {tracking['current_stage']}/{tracking['total_stages']} ({tracking['status_title']})")
    print(f"Next Action: {tracking['next_action']}")
