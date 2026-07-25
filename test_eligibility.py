import json
from agents.eligibility_agent import run_eligibility_agent, check_clarification_needed, parse_user_profile

def test_complete_profile():
    print("\n--- Test 1: Complete Profile (Farmer, Odisha, 1.5 LPA) ---")
    profile = {
        "age": 35,
        "gender": "male",
        "income_lpa": 1.5,
        "occupation": "farmer",
        "state": "Odisha",
        "caste_category": "OBC",
        "land_holding_acres": 2.0
    }
    res = run_eligibility_agent(profile)
    print(f"Needs Clarification: {res['needs_clarification']}")
    assert not res["needs_clarification"], "Complete profile should NOT trigger clarification"
    
    print(f"Summary: {res['summary']}")
    print("Matched Schemes:")
    for scheme in res["matched_schemes"]:
        print(f"  [OK] [{scheme['score']} pts] {scheme['id']}: {scheme['name']}")
    
    matched_ids = [s["id"] for s in res["matched_schemes"]]
    assert "pm-kisan" in matched_ids, "Farmer should be eligible for PM-KISAN"
    assert "ayushman-bharat" in matched_ids, "Low income should be eligible for Ayushman Bharat"

def test_incomplete_profile_missing_occupation():
    print("\n--- Test 2: Incomplete Profile (Missing Occupation) ---")
    profile = {
        "age": 30,
        "gender": "female",
        "income_lpa": 2.0,
        "occupation": None,
        "state": "Odisha"
    }
    res = run_eligibility_agent(profile)
    print(f"Needs Clarification: {res['needs_clarification']}")
    print(f"Clarification Question: {res['clarification_question']}")
    print(f"Missing Fields: {res['missing_fields']}")
    
    assert res["needs_clarification"], "Missing occupation SHOULD trigger clarification"
    assert "occupation" in res["missing_fields"]

def test_incomplete_profile_missing_income():
    print("\n--- Test 3: Incomplete Profile (Missing Income) ---")
    profile = {
        "age": 19,
        "gender": "female",
        "income_lpa": None,
        "occupation": "student",
        "state": "Odisha",
        "caste_category": "OBC"
    }
    res = run_eligibility_agent(profile)
    print(f"Needs Clarification: {res['needs_clarification']}")
    print(f"Clarification Question: {res['clarification_question']}")
    print(f"Missing Fields: {res['missing_fields']}")
    
    assert res["needs_clarification"], "Missing income SHOULD trigger clarification"
    assert "income_lpa" in res["missing_fields"]

def test_natural_language_instruction():
    print("\n--- Test 4: Natural Language Instruction ---")
    instruction = "I am a 22 year old female student from Odisha. My annual family income is 1.2 Lakhs."
    res = run_eligibility_agent(instruction)
    print("Parsed Profile:", json.dumps(res["user_profile"], indent=2))
    print(f"Needs Clarification: {res['needs_clarification']}")
    print(f"Summary: {res['summary']}")
    print("Matched Schemes:")
    for scheme in res["matched_schemes"]:
        print(f"  [OK] [{scheme['score']} pts] {scheme['id']}: {scheme['name']}")

if __name__ == "__main__":
    print("==========================================")
    print("Running Phase 2 Eligibility Agent Tests")
    print("==========================================")
    test_complete_profile()
    test_incomplete_profile_missing_occupation()
    test_incomplete_profile_missing_income()
    test_natural_language_instruction()
    print("\nALL PHASE 2 ELIGIBILITY AGENT TESTS PASSED SUCCESSFULLY!")
