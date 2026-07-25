import json
from orchestrator import run_orchestrator_pipeline

def test_full_pipeline_complete_profile():
    print("\n--- Test 1: Full Orchestration Pipeline (Complete Profile) ---")
    profile = {
        "name": "Ramesh Kumar",
        "age": 38,
        "gender": "male",
        "income_lpa": 1.5,
        "occupation": "farmer",
        "state": "Odisha",
        "caste_category": "OBC",
        "land_holding_acres": 2.0
    }

    state = run_orchestrator_pipeline(
        user_input=profile,
        language="English"
    )

    print(f"Instruction: {state['instruction']}")
    print(f"Needs Clarification: {state['needs_clarification']}")
    assert not state["needs_clarification"], "Complete profile should NOT trigger clarification"

    print(f"Matched Schemes Count: {len(state['matched_schemes'])}")
    assert len(state["matched_schemes"]) > 0, "Should match at least 1 scheme"

    print(f"Chosen Scheme ID: {state['chosen_scheme_id']}")
    assert state["chosen_scheme_id"] is not None

    print(f"Form Completion: {state['filled_form']['completion_percentage']}%")
    assert state["filled_form"] is not None

    print(f"Application Record ID: {state['application_record']['application_id']}")
    assert state["application_record"] is not None

    print("\nAction Log Preview (First 5 entries):")
    for log in state["action_log"][:5]:
        print(f"  [{log['timestamp']}] [{log['status']}] {log['agent']} -> {log['action']}: {log['reasoning']}")

    assert state["completed"], "Pipeline should report completed = True"
    print("  [OK] Full pipeline complete profile test passed!")

def test_pipeline_with_clarification():
    print("\n--- Test 2: Orchestration Pipeline (Clarification Path) ---")
    incomplete_profile = {
        "name": "Sunita Devi",
        "age": 29,
        "gender": "female",
        "income_lpa": 1.2,
        "occupation": None,  # Missing occupation!
        "state": "Odisha"
    }

    # Step 1: Initial run triggers clarification
    state = run_orchestrator_pipeline(
        user_input=incomplete_profile,
        language="Hindi"
    )

    print(f"Needs Clarification: {state['needs_clarification']}")
    print(f"Clarification Question: {state['clarification_question']}")
    assert state["needs_clarification"], "Incomplete profile MUST trigger clarification"
    assert not state["completed"], "Pipeline should pause before completion"

    # Step 2: User provides clarification response
    clarification_res = {"occupation": "farmer"}
    resumed_state = run_orchestrator_pipeline(
        user_input=incomplete_profile,
        language="Hindi",
        existing_state=state,
        clarification_response=clarification_res
    )

    print(f"Resumed Needs Clarification: {resumed_state['needs_clarification']}")
    assert not resumed_state["needs_clarification"], "Clarification should be resolved"
    assert resumed_state["completed"], "Resumed pipeline should complete cleanly"
    print(f"Application Record ID: {resumed_state['application_record']['application_id']}")

    print("  [OK] Pipeline clarification flow test passed!")

if __name__ == "__main__":
    test_full_pipeline_complete_profile()
    test_pipeline_with_clarification()
