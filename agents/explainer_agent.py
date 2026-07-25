import json
import os
from typing import Dict, Any, Optional, List, Union
from llm import call_llm
from agents.eligibility_agent import load_schemes

def get_scheme_by_id(scheme_id: str, schemes_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Helper to fetch a specific scheme from schemes.json by ID."""
    schemes = load_schemes(schemes_path)
    for scheme in schemes:
        if scheme["id"].lower() == scheme_id.lower():
            return scheme
    return None

def fallback_explanation(scheme: Dict[str, Any], language: str = "English") -> str:
    """Fallback plain-text explanation generated without LLM if API call fails."""
    is_hindi = str(language).lower() in ["hi", "hindi"]
    
    if is_hindi:
        return (
            f"📋 **योजना का नाम:** {scheme['name']}\n"
            f"🎯 **लक्ष्य:** {scheme.get('target_audience', 'पात्र नागरिक')}\n"
            f"💰 **मुख्य लाभ:** {scheme['benefits']}\n"
            f"📄 **आवश्यक दस्तावेज:** {', '.join(scheme.get('required_documents', []))}\n"
            f"🌐 **आधिकारिक पोर्टल:** {scheme.get('official_portal', 'N/A')}\n"
            f"📌 **आवेदन के चरण:** {scheme.get('application_steps', 'पोर्टल पर आवेदन करें।')}"
        )
    else:
        return (
            f"📋 **Scheme Name:** {scheme['name']}\n"
            f"🎯 **Target Group:** {scheme.get('target_audience', 'Eligible Citizens')}\n"
            f"💰 **Key Benefits:** {scheme['benefits']}\n"
            f"📄 **Required Documents:** {', '.join(scheme.get('required_documents', []))}\n"
            f"🌐 **Official Portal:** {scheme.get('official_portal', 'N/A')}\n"
            f"📌 **Application Steps:** {scheme.get('application_steps', 'Apply on official portal.')}"
        )

def explain_scheme(
    scheme_or_id: Union[str, Dict[str, Any]],
    language: str = "English",
    user_profile: Optional[Dict[str, Any]] = None,
    schemes_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Explainer Agent: Takes a scheme (ID or dict) and language preference,
    returning a personalized plain-language explanation.
    """
    if isinstance(scheme_or_id, str):
        scheme = get_scheme_by_id(scheme_or_id, schemes_path)
        if not scheme:
            return {
                "scheme_id": scheme_or_id,
                "language": language,
                "explanation": f"Scheme with ID '{scheme_or_id}' was not found.",
                "success": False
            }
    else:
        scheme = scheme_or_id

    is_hindi = str(language).lower() in ["hi", "hindi"]
    lang_instruction = "Respond entirely in Hindi (using Devanagari script)." if is_hindi else "Respond in clear, accessible English."

    profile_context = ""
    if user_profile:
        profile_context = (
            f"The user profile is: Occupation: {user_profile.get('occupation')}, "
            f"State: {user_profile.get('state')}, Income: {user_profile.get('income_lpa')} LPA, "
            f"Age: {user_profile.get('age')}, Gender: {user_profile.get('gender')}."
        )

    system_prompt = (
        "You are an empathetic, citizen-centric AI welfare assistant named SchemeSaathi. "
        "Your task is to explain a government welfare scheme to an Indian citizen in plain, warm, jargon-free language.\n"
        f"Language requirement: {lang_instruction}\n"
        "Format your output with clear markdown sections:\n"
        "1. **Summary & Benefits**: What the scheme gives them in simple terms.\n"
        "2. **Why You Qualify**: Personalized reason based on their profile.\n"
        "3. **What You Need**: List of required documents.\n"
        "4. **Next Steps**: Step-by-step guidance on how to get started."
    )

    user_prompt = (
        f"Scheme Details:\n"
        f"- Name: {scheme['name']}\n"
        f"- Category: {scheme['category']}\n"
        f"- Benefits: {scheme['benefits']}\n"
        f"- Eligibility: {json.dumps(scheme.get('eligibility', {}))}\n"
        f"- Required Documents: {', '.join(scheme.get('required_documents', []))}\n"
        f"- Application Steps: {scheme.get('application_steps', '')}\n"
        f"- Official Portal: {scheme.get('official_portal', '')}\n\n"
        f"{profile_context}\n"
        "Please explain this scheme clearly to the citizen now."
    )

    try:
        explanation_text = call_llm(prompt=user_prompt, system=system_prompt, max_retries=2)
        return {
            "scheme_id": scheme.get("id"),
            "scheme_name": scheme.get("name"),
            "language": "Hindi" if is_hindi else "English",
            "explanation": explanation_text,
            "required_documents": scheme.get("required_documents", []),
            "official_portal": scheme.get("official_portal", ""),
            "success": True,
            "source": "LLM"
        }
    except Exception as e:
        print(f"[ExplainerAgent] LLM explanation call failed ({e}). Falling back to raw scheme data.")
        fb_text = fallback_explanation(scheme, language)
        return {
            "scheme_id": scheme.get("id"),
            "scheme_name": scheme.get("name"),
            "language": "Hindi" if is_hindi else "English",
            "explanation": fb_text,
            "required_documents": scheme.get("required_documents", []),
            "official_portal": scheme.get("official_portal", ""),
            "success": True,
            "source": "Fallback"
        }

def explain_shortlist(
    matched_schemes: List[Dict[str, Any]],
    language: str = "English"
) -> str:
    """Generates a high-level summary overview of all matched schemes for the user."""
    if not matched_schemes:
        return "No matched schemes found to explain."
    
    is_hindi = str(language).lower() in ["hi", "hindi"]
    lang_instruction = "Respond entirely in Hindi." if is_hindi else "Respond in English."

    schemes_summary = "\n".join([f"- {s['name']}: {s.get('benefits')}" for s in matched_schemes[:5]])

    system_prompt = (
        "You are SchemeSaathi. Provide a brief 2-3 sentence encouraging overview summarizing "
        f"the citizen's eligible government schemes list. {lang_instruction}"
    )

    user_prompt = f"Matched schemes:\n{schemes_summary}\nSummarize these encouragingly for the user."

    try:
        return call_llm(prompt=user_prompt, system=system_prompt, max_retries=1)
    except Exception as e:
        if is_hindi:
            return f"आपकी प्रोफ़ाइल के आधार पर कुल {len(matched_schemes)} सरकारी योजनाएं पाई गई हैं। नीचे मुख्य विवरण देखें।"
        return f"Based on your profile, you are eligible for {len(matched_schemes)} government scheme(s). See key details below."

if __name__ == "__main__":
    print("Testing Explainer Agent in English...")
    res_en = explain_scheme("pm-kisan", language="English")
    print("--- English Explanation ---")
    print(res_en["explanation"])
    
    print("\nTesting Explainer Agent in Hindi...")
    res_hi = explain_scheme("pm-kisan", language="Hindi")
    print("--- Hindi Explanation ---")
    print(res_hi["explanation"])
