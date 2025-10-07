import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# ==============================================================================
# Constants
# ==============================================================================
# 16 bytes for AES-128, 24 bytes for AES-192, 32 bytes for AES-256
KEY_SIZE = 32
BLOCK_SIZE = AES.block_size 

def generate_key() -> bytes:
    """Generates a secure, random AES-256 encryption key."""
    return get_random_bytes(KEY_SIZE)

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """
    Encrypts raw bytes data using AES-256 in CBC mode.

    The Initialization Vector (IV) is prepended to the ciphertext.

    Args:
        data: The sensitive neurodata bytes to encrypt.
        key: The 32-byte encryption key.

    Returns:
        Encrypted data bytes (IV + Ciphertext).
    """
    try:
        # Generate a random 16-byte IV
        iv = get_random_bytes(BLOCK_SIZE) 
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Pad the data to be a multiple of the block size
        padded_data = pad(data, BLOCK_SIZE)
        
        ciphertext = cipher.encrypt(padded_data)
        
        # Prepend IV to ciphertext for decryption
        return iv + ciphertext
    except Exception as e:
        print(f"Encryption failed: {e}")
        # In production, handle failure gracefully (e.g., secure wipe)
        return data # Fallback, but dangerous

def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """
    Decrypts AES-256 CBC encrypted data.

    Args:
        encrypted_data: The IV + Ciphertext bytes.
        key: The 32-byte encryption key.

    Returns:
        Decrypted plaintext data bytes.
    """
    try:
        # Separate IV and ciphertext
        iv = encrypted_data[:BLOCK_SIZE]
        ciphertext = encrypted_data[BLOCK_SIZE:]
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded_data = cipher.decrypt(ciphertext)
        
        # Unpad the data
        plaintext = unpad(decrypted_padded_data, BLOCK_SIZE)
        
        return plaintext
    except Exception as e:
        print(f"Decryption failed. Data may be corrupt or key is incorrect: {e}")
        return b''

def secure_local_save(data_to_save: str, filepath: str, key: bytes):
    """
    Encrypts and saves the sensitive data locally, ensuring it never leaves
    the device unencrypted.

    Args:
        data_to_save: The string data (e.g., JSON report) to be saved.
        filepath: Local file path on the wearable/phone storage.
        key: The encryption key.
    """
    data_bytes = data_to_save.encode('utf-8')
    encrypted_bytes = encrypt_data(data_bytes, key)
    
    with open(filepath, 'wb') as f:
        f.write(encrypted_bytes)
    
    print(f"Successfully encrypted and saved data to {filepath}")


# Example Usage:
if __name__ == "__main__":
    # 1. Generate a Key (Stored securely on device/backend)
    device_key = generate_key()
    print(f"Generated Key (Base64 encoded): {base64.b64encode(device_key).decode()}")

    # 2. Mock Sensitive Data (e.g., raw neurodata snapshot)
    sensitive_report = '{"user_id": "NS_USER_123", "session_id": "A-456", "risk_score": 75, "raw_data_hash": "abc123def456"}'
    
    # 3. Encrypt Data
    encrypted_content = encrypt_data(sensitive_report.encode('utf-8'), device_key)
    print(f"Encrypted data size: {len(encrypted_content)} bytes")

    # 4. Decrypt Data
    decrypted_content = decrypt_data(encrypted_content, device_key)
    print(f"Decrypted content: {decrypted_content.decode('utf-8')}")

    assert sensitive_report == decrypted_content.decode('utf-8'), "Encryption/Decryption failed consistency check!"

    # 5. Secure Local Save Demonstration
    mock_filepath = "temp_neurodata.enc"
    secure_local_save(sensitive_report, mock_filepath, device_key)

    # 6. Read and Decrypt File (Simulating next access)
    with open(mock_filepath, 'rb') as f:
        encrypted_from_file = f.read()
    
    decrypted_from_file = decrypt_data(encrypted_from_file, device_key)
    print(f"Decrypted from file: {decrypted_from_file.decode('utf-8')}")
    
    # Clean up mock file
    if os.path.exists(mock_filepath):
        os.remove(mock_filepath)
