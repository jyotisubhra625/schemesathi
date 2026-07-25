import json
import os
from typing import Dict, Any, Optional

DEFAULT_PROFILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_profile.json")

def save_user_profile(profile: Dict[str, Any], filepath: Optional[str] = None) -> str:
    """Saves user profile to local disk."""
    path = filepath or DEFAULT_PROFILE_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    return path

def load_user_profile(filepath: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Loads user profile from local disk if it exists."""
    path = filepath or DEFAULT_PROFILE_PATH
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ProfileManager] Warning: Failed to read profile from {path}: {e}")
        return None

def clear_user_profile(filepath: Optional[str] = None) -> bool:
    """Clears saved profile from local disk."""
    path = filepath or DEFAULT_PROFILE_PATH
    if os.path.exists(path):
        try:
            os.remove(path)
            return True
        except Exception as e:
            print(f"[ProfileManager] Warning: Failed to delete {path}: {e}")
            return False
    return False

def has_saved_profile(filepath: Optional[str] = None) -> bool:
    """Checks if a saved profile exists."""
    path = filepath or DEFAULT_PROFILE_PATH
    return os.path.exists(path)

if __name__ == "__main__":
    test_prof = {"name": "Subhra", "age": 25, "state": "Odisha"}
    p = save_user_profile(test_prof)
    print("Saved to:", p)
    loaded = load_user_profile()
    print("Loaded:", loaded)
    clear_user_profile()
    print("Has saved after clear:", has_saved_profile())
