from cryptography.fernet import Fernet
import os

def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.key", "rb").read()

def get_fernet():
    # Check if key file exists and has content
    if not os.path.exists("secret.key") or os.path.getsize("secret.key") == 0:
        print("Generating new encryption key...")
        generate_key()
        print("✅ Key generated successfully!")
    
    key = load_key()
    return Fernet(key)

# Add this test block
if __name__ == "__main__":
    print("Testing encryption system...")
    
    # Test key generation/loading
    fernet = get_fernet()
    print("✅ Encryption key ready!")
    
    # Test encryption/decryption
    test_message = "test password 123"
    encrypted = fernet.encrypt(test_message.encode())
    decrypted = fernet.decrypt(encrypted).decode()
    
    print(f"Original: {test_message}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    
    if test_message == decrypted:
        print("✅ Encryption test passed!")
    else:
        print("❌ Encryption test failed!")
