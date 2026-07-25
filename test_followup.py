import os
from agents.followup_agent import create_application_record, track_application, get_demo_followup_summary

def test_create_application_record():
    print("\n--- Test 1: Create Application Record ---")
    rec = create_application_record("pm-kisan", applicant_name="Ramesh Kumar")
    print(f"App ID: {rec['application_id']}")
    print(f"Scheme: {rec['scheme_name']}")
    print(f"Status: {rec['current_status']}")

    assert rec["application_id"].startswith("APP-")
    assert rec["current_stage"] == 1
    assert "PM-KISAN" in rec["scheme_name"]
    print("  [OK] Application creation passed!")

def test_track_application():
    print("\n--- Test 2: Track Application Progression ---")
    app_id = "APP-2026-PMKI-54321"
    
    # Track stage 2
    track2 = track_application(app_id, stage_override=2)
    print(f"Stage 2 Status: {track2['status_title']} ({track2['status_description']})")
    assert track2["current_stage"] == 2
    assert track2["timeline"][0]["status"] == "Completed"
    assert track2["timeline"][1]["status"] == "In Progress"
    assert track2["timeline"][2]["status"] == "Pending"

    # Track stage 4 (Disbursal complete)
    track4 = track_application(app_id, stage_override=4)
    print(f"Stage 4 Status: {track4['status_title']}")
    assert track4["is_complete"]
    print("  [OK] Application stage progression tracking passed!")

def test_demo_followup_summary():
    print("\n--- Test 3: Application Follow-up Dashboard Summary ---")
    summary = get_demo_followup_summary("Priya Mohanty")
    print(f"Total Applications Tracked: {len(summary)}")
    for app in summary:
        print(f"  - {app['application_id']}: {app['scheme_name']} [{app['current_status']}]")
    
    assert len(summary) >= 2
    print("  [OK] Demo dashboard summary passed!")

if __name__ == "__main__":
    print("==========================================")
    print("Running Phase 5 Follow-up Agent Tests")
    print("==========================================")
    test_create_application_record()
    test_track_application()
    test_demo_followup_summary()
    print("\nALL PHASE 5 FOLLOW-UP AGENT TESTS PASSED SUCCESSFULLY!")
