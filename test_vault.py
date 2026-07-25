import os
from vault.crypto_utils import encrypt_bytes, decrypt_bytes, derive_key
from vault.vault_manager import upload_document, check_scheme_documents, read_decrypted_document, get_uploaded_document_labels, load_vault_index, save_vault_index

def test_crypto_primitives():
    print("\n--- Test 1: Crypto Primitives (PBKDF2 + AES-256 Fernet) ---")
    passphrase = "mySecretVaultPassword123"
    raw_data = b"Sample Sensitive Document Bytes: Aadhaar # 1234-5678-9012"

    enc = encrypt_bytes(passphrase, raw_data)
    assert enc != raw_data, "Encrypted data must not match raw data"

    dec = decrypt_bytes(passphrase, enc)
    assert dec == raw_data, "Decrypted data must match original raw data"
    print("  [OK] Encryption & decryption verified!")

    # Test wrong passphrase
    try:
        decrypt_bytes("wrongPassphrase", enc)
        assert False, "Should have failed with wrong passphrase"
    except ValueError as e:
        print("  [OK] Wrong passphrase correctly rejected:", e)

def test_vault_upload_and_check():
    print("\n--- Test 2: Vault Document Upload & Scheme Reuse Check ---")
    # Clean index for test
    save_vault_index({})

    passphrase = "passphrase2026"
    up1 = upload_document(passphrase, b"Dummy Aadhaar File Content", "Aadhaar Card")
    assert up1["success"]
    assert up1["label"] == "Aadhaar Card"

    up2 = upload_document(passphrase, b"Dummy Land Record Content", "Land Record")
    assert up2["success"]

    up3 = upload_document(passphrase, b"Custom Income Cert", "Other", custom_label="Income Certificate")
    assert up3["label"] == "Income Certificate"

    labels = get_uploaded_document_labels()
    print("Uploaded Labels in Vault:", labels)
    assert "Aadhaar Card" in labels
    assert "Land Record" in labels
    assert "Income Certificate" in labels

    # Simulate PM-KISAN requiring ["Aadhaar Card", "Land Record", "Bank Passbook"]
    req = ["Aadhaar Card", "Land Record", "Bank Passbook"]
    chk = check_scheme_documents(req)
    print("Present Docs:", [p["found_label"] for p in chk["present_documents"]])
    print("Missing Docs:", chk["missing_documents"])

    assert len(chk["present_documents"]) == 2
    assert "Bank Passbook" in chk["missing_documents"]
    print("  [OK] Scheme document presence check passed!")

    # Decrypt uploaded document
    dec_aadhaar = read_decrypted_document(passphrase, "Aadhaar Card")
    assert dec_aadhaar == b"Dummy Aadhaar File Content"
    print("  [OK] Decrypted document content verified!")

if __name__ == "__main__":
    print("==========================================")
    print("Running Phase 5a Document Vault Tests")
    print("==========================================")
    test_crypto_primitives()
    test_vault_upload_and_check()
    print("\nALL PHASE 5A DOCUMENT VAULT TESTS PASSED SUCCESSFULLY!")
