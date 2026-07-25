import os
import json
import re
from typing import Dict, Any, List, Optional
from vault.crypto_utils import encrypt_file, decrypt_file, STORAGE_DIR, VAULT_DIR

INDEX_FILE = os.path.join(VAULT_DIR, "vault_index.json")

STANDARD_DOCUMENT_DROPDOWN = [
    "Aadhaar Card",
    "PAN Card",
    "Birth Certificate",
    "Land Record",
    "Bank Passbook",
    "Income Certificate",
    "Caste Certificate",
    "Domicile Certificate",
    "Ration Card",
    "MGNREGA Job Card",
    "Other"
]

def load_vault_index() -> Dict[str, str]:
    """Loads vault_index.json mapping label -> encrypted_filename."""
    if not os.path.exists(INDEX_FILE):
        return {}
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_vault_index(index_data: Dict[str, str]):
    """Saves vault_index.json."""
    os.makedirs(VAULT_DIR, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

def label_to_filename(label: str) -> str:
    """Converts a user-facing document label to a clean file basename."""
    clean = re.sub(r"[^\w\-]", "_", label.lower()).strip("_")
    return f"{clean}.enc"

def upload_document(
    passphrase: str,
    file_bytes: bytes,
    label: str,
    custom_label: Optional[str] = None
) -> Dict[str, Any]:
    """
    Encrypts and saves a user document.
    Updates vault_index.json with document label -> filename mapping.
    """
    final_label = custom_label.strip() if label == "Other" and custom_label else label.strip()
    if not final_label:
        raise ValueError("Document label cannot be empty.")

    out_filename = label_to_filename(final_label)
    enc_path = encrypt_file(passphrase, file_bytes, out_filename)

    index = load_vault_index()
    index[final_label] = out_filename
    save_vault_index(index)

    return {
        "label": final_label,
        "filename": out_filename,
        "filepath": enc_path,
        "success": True
    }

def get_uploaded_document_labels() -> List[str]:
    """Returns list of all document labels stored in the vault."""
    index = load_vault_index()
    return list(index.keys())

def check_scheme_documents(required_docs: List[str]) -> Dict[str, Any]:
    """
    Checks vault_index.json against scheme required documents.
    Returns present documents vs missing documents without needing decryption.
    """
    index = load_vault_index()
    uploaded_labels_lower = {k.lower(): k for k in index.keys()}

    present = []
    missing = []

    for doc in required_docs:
        doc_clean = doc.lower()
        matched = False
        for u_clean, u_label in uploaded_labels_lower.items():
            if doc_clean in u_clean or u_clean in doc_clean:
                present.append({"required": doc, "found_label": u_label})
                matched = True
                break
        if not matched:
            missing.append(doc)

    return {
        "required_documents": required_docs,
        "present_documents": present,
        "missing_documents": missing,
        "all_present": len(missing) == 0
    }

def read_decrypted_document(passphrase: str, label: str) -> bytes:
    """Decrypts and returns file bytes for a specific document label."""
    index = load_vault_index()
    if label not in index:
        raise FileNotFoundError(f"Document label '{label}' not found in vault index.")
    
    filename = index[label]
    filepath = os.path.join(STORAGE_DIR, filename)
    return decrypt_file(passphrase, filepath)

def delete_document(label: str) -> bool:
    """Removes encrypted file from disk and updates index."""
    index = load_vault_index()
    if label in index:
        filename = index[label]
        filepath = os.path.join(STORAGE_DIR, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass
        del index[label]
        save_vault_index(index)
        return True
    return False

def verify_vault_passphrase(passphrase: str) -> bool:
    """
    Validates passphrase against existing files in vault.
    Returns True if valid key or empty vault; False if decryption fails.
    """
    index = load_vault_index()
    if not index:
        return True
    first_label = next(iter(index.keys()))
    try:
        read_decrypted_document(passphrase, first_label)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    passphrase = "mySecretPassword123"
    upload_document(passphrase, b"Aadhaar File Content", "Aadhaar Card")
    upload_document(passphrase, b"Land Record File Content", "Land Record")

    chk = check_scheme_documents(["Aadhaar Card", "Land Record", "Birth Certificate"])
    print("Present Docs:", chk["present_documents"])
    print("Missing Docs:", chk["missing_documents"])
    print("All Present:", chk["all_present"])
