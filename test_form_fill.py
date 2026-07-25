import os
import json
from agents.profile_manager import save_user_profile, clear_user_profile
from agents.form_fill_agent import fill_form

def test_full_form_fill():
    print("\n--- Test 1: Full Form Auto-Fill (PM-KISAN) ---")
    profile = {
        "name": "Sita Devi",
        "age": 42,
        "gender": "female",
        "state": "Odisha",
        "occupation": "farmer",
        "income_lpa": 1.2,
        "land_holding_acres": 1.5,
        "khata_khatian_no": "Khata 145/2",
        "aadhaar_number": "1234-5678-9012",
        "bank_account_number": "112233445566",
        "bank_ifsc": "SBIN000456"
    }

    res = fill_form("pm-kisan", user_profile=profile)
    print(f"Scheme: {res['scheme_name']}")
    print(f"Completion: {res['completion_percentage']}%")
    print(f"Ready for Submission: {res['ready_for_submission']}")
    print(f"Missing Fields Count: {len(res['missing_fields'])}")

    assert res["completion_percentage"] == 100.0
    assert res["ready_for_submission"]
    assert len(res["missing_fields"]) == 0
    print("  [OK] Full auto-fill passed with 100% completion!")

def test_partial_form_fill():
    print("\n--- Test 2: Partial Form Auto-Fill with Missing Fields (Ayushman Bharat) ---")
    profile = {
        "name": "Rohan Das",
        "age": 28,
        "gender": "male",
        "state": "Odisha",
        "occupation": "student",
        "income_lpa": 1.0,
        "aadhaar_number": "9876-5432-1098"
        # Missing: bank_account_number, bank_ifsc, ration_card_number
    }

    res = fill_form("ayushman-bharat", user_profile=profile)
    print(f"Scheme: {res['scheme_name']}")
    print(f"Completion: {res['completion_percentage']}%")
    print(f"Ready for Submission: {res['ready_for_submission']}")
    print(f"Missing Fields:")
    for mf in res["missing_fields"]:
        print(f"  - {mf['label']} ({mf['field_key']})")

    assert not res["ready_for_submission"]
    assert len(res["missing_fields"]) > 0
    missing_keys = [m["field_key"] for m in res["missing_fields"]]
    assert "ration_card_number" in missing_keys
    print("  [OK] Partial auto-fill correctly flagged missing fields!")

def test_persistent_profile_form_fill():
    print("\n--- Test 3: Form Fill using Persistent Profile ---")
    clear_user_profile()
    save_user_profile({
        "name": "Priya Mohanty",
        "age": 24,
        "gender": "female",
        "state": "Odisha",
        "occupation": "student",
        "income_lpa": 1.2,
        "caste_category": "OBC",
        "aadhaar_number": "5555-6666-7777",
        "bank_account_number": "999888777666",
        "bank_ifsc": "BARB0ODISHA",
        "institution_name": "Utkal University",
        "marksheet_percentage": "82%"
    })

    # Call fill_form without passing user_profile argument
    res = fill_form("post-matric-scholarship")
    print(f"Scheme: {res['scheme_name']}")
    print(f"Completion: {res['completion_percentage']}%")
    print(f"Ready for Submission: {res['ready_for_submission']}")

    assert res["completion_percentage"] == 100.0
    assert res["filled_fields"]["applicant_name"]["value"] == "Priya Mohanty"
    print("  [OK] Form-Fill Agent successfully auto-filled from persistent profile store!")
    clear_user_profile()

if __name__ == "__main__":
    print("==========================================")
    print("Running Phase 4 Form-Fill Agent Tests")
    print("==========================================")
    test_full_form_fill()
    test_partial_form_fill()
    test_persistent_profile_form_fill()
    print("\nALL PHASE 4 FORM-FILL AGENT TESTS PASSED SUCCESSFULLY!")
