import json
import os
import re
from typing import Dict, List, Any, Optional, Union
from llm import call_llm
from agents.profile_manager import save_user_profile, load_user_profile, has_saved_profile

DEFAULT_SCHEMES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "schemes.json")

def load_schemes(schemes_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Loads schemes from JSON file."""
    path = schemes_path or DEFAULT_SCHEMES_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Schemes file not found at: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_user_profile(user_input: str) -> Dict[str, Any]:
    """
    Parses natural language user input into a structured profile dict using LLM.
    """
    system_prompt = (
        "You are an expert profile extractor for Indian welfare schemes. "
        "Extract citizen profile information from the user instruction and return ONLY a valid JSON object. "
        "Do NOT include markdown formatting or extra text outside the JSON.\n\n"
        "Required JSON fields:\n"
        "{\n"
        '  "age": int or null,\n'
        '  "gender": "male" | "female" | "other" | null,\n'
        '  "income_lpa": float (annual income in Lakhs) or null,\n'
        '  "occupation": "farmer" | "artisan" | "student" | "street_vendor" | "entrepreneur" | "self_employed" | str or null,\n'
        '  "state": str (e.g. "Odisha", "Maharashtra") or null,\n'
        '  "caste_category": "SC" | "ST" | "OBC" | "General" | null,\n'
        '  "land_holding_acres": float or null,\n'
        '  "has_pucca_house": bool or null,\n'
        '  "is_pregnant_or_lactating": bool or null,\n'
        '  "has_bpl_card": bool or null\n'
        "}"
    )

    try:
        response_text = call_llm(prompt=user_input, system=system_prompt)
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))
            return sanitize_profile(parsed)
    except Exception as e:
        print(f"[EligibilityAgent] Warning: LLM profile parsing failed ({e}). Falling back to empty profile.")

    return {
        "age": None,
        "gender": None,
        "income_lpa": None,
        "occupation": None,
        "state": None,
        "caste_category": None,
        "land_holding_acres": None,
        "has_pucca_house": None,
        "is_pregnant_or_lactating": None,
        "has_bpl_card": None
    }

def sanitize_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures profile fields are cast to appropriate numeric/bool types safely."""
    if not isinstance(profile, dict):
        return {}

    sanitized = dict(profile)

    # Sanitize Age
    age_raw = sanitized.get("age")
    if age_raw is not None and not isinstance(age_raw, (int, float)):
        try:
            sanitized["age"] = int(float(str(age_raw).strip()))
        except (ValueError, TypeError):
            sanitized["age"] = None

    # Sanitize Income
    inc_raw = sanitized.get("income_lpa")
    if inc_raw is not None and not isinstance(inc_raw, (int, float)):
        try:
            sanitized["income_lpa"] = float(str(inc_raw).strip())
        except (ValueError, TypeError):
            sanitized["income_lpa"] = None

    # Sanitize Land Holding
    land_raw = sanitized.get("land_holding_acres")
    if land_raw is not None and not isinstance(land_raw, (int, float)):
        try:
            sanitized["land_holding_acres"] = float(str(land_raw).strip())
        except (ValueError, TypeError):
            sanitized["land_holding_acres"] = None

    return sanitized

def check_clarification_needed(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Checks if key fields (occupation, income_lpa, state) are missing or ambiguous.
    Asks a single targeted follow-up question if clarification is needed.
    """
    missing_fields = []
    
    # Check occupation
    occ = user_profile.get("occupation")
    if not occ or str(occ).strip().lower() in ["none", "null", "unknown", "any"]:
        missing_fields.append("occupation")

    # Check income
    inc = user_profile.get("income_lpa")
    if inc is None or str(inc).strip().lower() in ["none", "null", "unknown"]:
        missing_fields.append("income_lpa")

    # Check state
    st = user_profile.get("state")
    if not st or str(st).strip().lower() in ["none", "null", "unknown", "all"]:
        missing_fields.append("state")

    if not missing_fields:
        return {
            "needs_clarification": False,
            "clarification_question": None,
            "missing_fields": []
        }

    # Formulate single follow-up question based on missing fields
    if "occupation" in missing_fields and "income_lpa" in missing_fields:
        question = "Could you please tell me your primary occupation (e.g., farmer, student, artisan, street vendor, self-employed) and your approximate annual family income (in Lakhs)?"
    elif "occupation" in missing_fields:
        question = "Could you please specify your current occupation (e.g., farmer, student, artisan, street vendor, self-employed, or homemaker)?"
    elif "income_lpa" in missing_fields:
        question = "Could you please share your approximate annual family income in Lakhs (e.g., 1.5, 2.5)?"
    elif "state" in missing_fields:
        question = "Which state do you currently reside in (e.g., Odisha, Maharashtra, Bihar)?"
    else:
        question = f"Could you please provide your {', '.join(missing_fields)} to help match the exact schemes for you?"

    return {
        "needs_clarification": True,
        "clarification_question": question,
        "missing_fields": missing_fields
    }

def evaluate_eligibility(
    user_profile: Dict[str, Any],
    schemes: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates profile against schemes and returns list of scheme evaluation results
    sorted by match score.
    """
    if schemes is None:
        schemes = load_schemes()

    results = []

    user_age = user_profile.get("age")
    user_gender = str(user_profile.get("gender") or "").lower()
    user_income = user_profile.get("income_lpa")
    user_occ = str(user_profile.get("occupation") or "").lower()
    user_state = str(user_profile.get("state") or "").lower()
    user_caste = str(user_profile.get("caste_category") or "").upper()
    user_land = user_profile.get("land_holding_acres")

    for scheme in schemes:
        elig = scheme.get("eligibility", {})
        score = 100
        eligible = True
        reasons = []
        warnings = []

        # 1. Occupation Check
        req_occ = str(elig.get("occupation", "any")).lower()
        if req_occ != "any":
            if not user_occ:
                warnings.append("Occupation unspecified")
            elif req_occ not in user_occ and user_occ not in req_occ:
                # Special mapping checks
                occ_matches = False
                if req_occ == "entrepreneur" and user_occ in ["self_employed", "business"]:
                    occ_matches = True
                elif req_occ == "artisan" and user_occ in ["craftsman", "weaver", "tailor", "carpenter"]:
                    occ_matches = True
                elif req_occ == "farmer" and user_occ in ["agriculture", "cultivator"]:
                    occ_matches = True
                
                if not occ_matches:
                    eligible = False
                    score -= 50
                    reasons.append(f"Requires occupation '{req_occ}', but profile is '{user_occ}'")
            else:
                reasons.append(f"Occupation matches '{req_occ}'")

        # 2. Income Check
        max_income = elig.get("max_income_lpa")
        if max_income is not None:
            if user_income is None:
                warnings.append(f"Income cap is ₹{max_income} LPA (profile unspecified)")
            elif user_income > max_income:
                eligible = False
                score -= 40
                reasons.append(f"Annual income ₹{user_income} LPA exceeds scheme cap of ₹{max_income} LPA")
            else:
                reasons.append(f"Income ₹{user_income} LPA is within limit of ₹{max_income} LPA")

        # 3. Age Check
        min_age = elig.get("min_age")
        max_age = elig.get("max_age")
        if min_age is not None and user_age is not None and user_age < min_age:
            eligible = False
            score -= 30
            reasons.append(f"Age {user_age} is below minimum age of {min_age}")
        if max_age is not None and user_age is not None and user_age > max_age:
            eligible = False
            score -= 30
            reasons.append(f"Age {user_age} exceeds maximum age of {max_age}")
        if (min_age is not None or max_age is not None) and user_age is not None and eligible:
            reasons.append(f"Age {user_age} satisfies age range ({min_age or 0}-{max_age or 'no cap'})")

        # 4. Gender Check
        req_gender = str(elig.get("gender", "any")).lower()
        if req_gender != "any":
            if not user_gender:
                warnings.append(f"Scheme is for '{req_gender}' (profile gender unspecified)")
            elif user_gender != req_gender:
                eligible = False
                score -= 40
                reasons.append(f"Scheme is exclusively for '{req_gender}', profile is '{user_gender}'")
            else:
                reasons.append(f"Gender matches '{req_gender}'")

        # 5. State Check
        req_state = str(elig.get("state", "all")).lower()
        if req_state != "all":
            if not user_state:
                warnings.append(f"State specific to '{req_state.title()}'")
            elif user_state != req_state:
                eligible = False
                score -= 50
                reasons.append(f"Scheme restricted to '{req_state.title()}', user state is '{user_state.title()}'")
            else:
                reasons.append(f"State matches '{req_state.title()}'")

        # 6. Land Holding Check
        max_land = elig.get("land_holding_max_acres")
        if max_land is not None and user_land is not None:
            if user_land > max_land:
                eligible = False
                score -= 30
                reasons.append(f"Land holding {user_land} acres exceeds limit of {max_land} acres")

        # 7. Caste Category Check
        req_caste = str(elig.get("caste_category", "all")).upper()
        if req_caste != "ALL" and user_caste:
            if "SC" in req_caste and user_caste not in ["SC", "ST", "OBC"]:
                eligible = False
                score -= 30
                reasons.append(f"Scheme for {req_caste}, user category is {user_caste}")

        # Final Score adjustment
        score = max(0, score)
        if not eligible:
            status = "Ineligible"
        elif warnings:
            status = "Potentially Eligible"
        else:
            status = "Eligible"

        results.append({
            "id": scheme["id"],
            "name": scheme["name"],
            "category": scheme["category"],
            "status": status,
            "eligible": eligible,
            "score": score,
            "benefits": scheme["benefits"],
            "reasons": reasons,
            "warnings": warnings,
            "required_documents": scheme.get("required_documents", [])
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def run_eligibility_agent(
    user_input: Optional[Union[str, Dict[str, Any]]] = None,
    schemes_path: Optional[str] = None,
    use_saved_profile: bool = False
) -> Dict[str, Any]:
    """
    Main entry point for Eligibility Agent.
    Input can be a raw instruction string, structured profile dict, or None (to load saved profile).
    Returns evaluation results and conditional clarification triggers.
    """
    if use_saved_profile or user_input is None:
        saved = load_user_profile()
        if saved:
            profile = sanitize_profile(saved)
        elif isinstance(user_input, str):
            profile = parse_user_profile(user_input)
        elif isinstance(user_input, dict):
            profile = sanitize_profile(user_input)
        else:
            profile = {}
    elif isinstance(user_input, str):
        extracted = parse_user_profile(user_input)
        saved = load_user_profile() or {}
        # Start with saved profile, then overwrite with any explicitly extracted fields from prompt
        profile = dict(saved)
        for k, v in extracted.items():
            if v is not None:
                profile[k] = v
        profile = sanitize_profile(profile)
    else:
        profile = sanitize_profile(user_input)

    schemes = load_schemes(schemes_path)
    clarification = check_clarification_needed(profile)
    evaluations = evaluate_eligibility(profile, schemes)

    matched_schemes = [s for s in evaluations if s["eligible"]]

    # Auto-save profile if it contains useful details
    if profile:
        save_user_profile(profile)

    return {
        "user_profile": profile,
        "needs_clarification": clarification["needs_clarification"],
        "clarification_question": clarification["clarification_question"],
        "missing_fields": clarification["missing_fields"],
        "matched_schemes": matched_schemes,
        "evaluated_schemes": evaluations,
        "summary": f"Found {len(matched_schemes)} eligible scheme(s) out of {len(schemes)} total schemes evaluated."
    }

if __name__ == "__main__":
    print("Testing Eligibility Agent...")
    sample_profile = {
        "age": 35,
        "gender": "male",
        "income_lpa": 1.5,
        "occupation": "farmer",
        "state": "Odisha",
        "caste_category": "OBC",
        "land_holding_acres": 2.0
    }
    result = run_eligibility_agent(sample_profile)
    print("Needs Clarification:", result["needs_clarification"])
    print("Summary:", result["summary"])
    print("Top Matched Schemes:")
    for s in result["matched_schemes"][:3]:
        print(f" - [{s['score']} pts] {s['name']} ({s['status']})")
