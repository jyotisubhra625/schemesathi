import os
import json
from agents.profile_manager import save_user_profile, load_user_profile, clear_user_profile, has_saved_profile
from agents.eligibility_agent import run_eligibility_agent
from agents.explainer_agent import explain_scheme, explain_shortlist

def test_profile_persistence():
    print("\n--- Test 1: Local Profile Persistence ---")
    clear_user_profile()
    assert not has_saved_profile(), "Profile should be clear initially"

    test_prof = {
        "age": 35,
        "gender": "male",
        "income_lpa": 1.5,
        "occupation": "farmer",
        "state": "Odisha"
    }

    # Run agent - auto-saves profile
    res1 = run_eligibility_agent(test_prof)
    assert has_saved_profile(), "Profile should be saved after running eligibility agent"

    # Reload from disk
    loaded = load_user_profile()
    assert loaded["occupation"] == "farmer"
    assert loaded["state"] == "Odisha"
    print("  [OK] Profile saved and successfully reloaded from disk.")

    # Re-run using saved profile without passing user_input
    res2 = run_eligibility_agent(use_saved_profile=True)
    assert res2["user_profile"]["occupation"] == "farmer"
    assert len(res2["matched_schemes"]) > 0
    print("  [OK] Successfully executed eligibility evaluation using persistent saved profile!")

    clear_user_profile()
    print("  [OK] Profile cleared.")

def test_explainer_agent_english():
    print("\n--- Test 2: Explainer Agent (English) ---")
    res = explain_scheme("pm-kisan", language="English", user_profile={"occupation": "farmer", "state": "Odisha"})
    print("Source:", res["source"])
    clean_snippet = res["explanation"][:250].encode("ascii", "ignore").decode("ascii")
    print("Explanation Snippet:\n", clean_snippet, "...")
    assert res["success"]
    assert "PM-KISAN" in res["scheme_name"] or "pm-kisan" in res["scheme_id"]

def test_explainer_agent_hindi():
    print("\n--- Test 3: Explainer Agent (Hindi) ---")
    res = explain_scheme("ayushman-bharat", language="Hindi", user_profile={"income_lpa": 1.5})
    print("Source:", res["source"])
    clean_snippet = res["explanation"][:250].encode("ascii", "ignore").decode("ascii")
    print("Hindi Explanation Snippet (ASCII sanitized):\n", clean_snippet, "...")
    assert res["success"]
    assert res["language"] == "Hindi"

def test_explainer_fallback():
    print("\n--- Test 4: Explainer Fallback Mode ---")
    # Test fallback directly
    from agents.explainer_agent import fallback_explanation, get_scheme_by_id
    scheme = get_scheme_by_id("pmay-g")
    fb_en = fallback_explanation(scheme, language="English")
    clean_en = fb_en[:200].encode("ascii", "ignore").decode("ascii")
    print("Fallback English:\n", clean_en)
    assert "PMAY-G" in fb_en
    fb_hi = fallback_explanation(scheme, language="Hindi")
    clean_hi = fb_hi[:200].encode("ascii", "ignore").decode("ascii")
    print("Fallback Hindi:\n", clean_hi)
    assert "योजना का नाम" in fb_hi

if __name__ == "__main__":
    print("==========================================")
    print("Running Profile Persistence & Explainer Tests")
    print("==========================================")
    test_profile_persistence()
    test_explainer_agent_english()
    test_explainer_agent_hindi()
    test_explainer_fallback()
    print("\nALL PERSISTENCE & EXPLAINER AGENT TESTS PASSED SUCCESSFULLY!")
