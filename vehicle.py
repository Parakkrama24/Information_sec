import socket
import json
import os
import time
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Constants
HOST = '127.0.0.1'
PORT = 65432
CHALLENGE_SIZE = 32

def load_keys():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("vehicle_private.pem", "rb") as key_file:
        vehicle_private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    with open("edge_server_public.pem", "rb") as key_file:
        server_public_key = serialization.load_pem_public_key(
            key_file.read()
        )
    return vehicle_private_key, server_public_key

def main():
    print("Starting Vehicle Node...")
    try:
        vehicle_private_key, server_public_key = load_keys()
        print("Keys loaded successfully.")
    except Exception as e:
        print(f"Error loading keys. Have you run keys_setup.py? {e}")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"Connected to Edge Server at {HOST}:{PORT}")
        except ConnectionRefusedError:
            print("Failed to connect to Edge Server. Is it running?")
            return
            
        # --- Phase 2: Mutual Authentication (Challenge-Response) ---
        print("Waiting for Challenge from Edge Server...")
        challenge = s.recv(CHALLENGE_SIZE)
        
        print("Signing Challenge...")
        signature = vehicle_private_key.sign(
            challenge,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Sending Challenge Signature back to Edge Server...")
        s.sendall(signature)
        
        # Add slight delay to avoid socket packet merging in this simple implementation
        time.sleep(0.5)
        
        # --- Phase 3: Key Exchange (Session Key Generation) ---
        print("Generating random 256-bit AES Session Key...")
        aes_session_key = AESGCM.generate_key(bit_length=256)
        
        print("Encrypting AES Session Key with Edge Server's Public RSA Key...")
        encrypted_session_key = server_public_key.encrypt(
            aes_session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print("Sending Encrypted AES Session Key...")
        s.sendall(encrypted_session_key)
        
        time.sleep(0.5)
        
        # --- Phase 4: Secure State Dissemination ---
        print("Preparing Vehicle State Telemetry...")
        state_data = {
            "vehicle_id": "V-4848",
            "position": {"x": 42.3601, "y": -71.0589},
            "velocity": 65.5,
            "qos_level": 2,
            "privacy_demand_psi": 0.85
        }
        json_data = json.dumps(state_data).encode('utf-8')
        
        print("Signing Vehicle State payload (Non-repudiation)...")
        payload_signature = vehicle_private_key.sign(
            json_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        print("Encrypting Vehicle State payload with AES-GCM (Confidentiality & Integrity)...")
        aesgcm = AESGCM(aes_session_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, json_data, None)
        
        print("Sending Secure Package to Edge Server...")
        # Package structure: 12 bytes nonce + ciphertext (payload+mac) + 256 bytes signature
        secure_package = nonce + ciphertext + payload_signature
        s.sendall(secure_package)
        
        print("Vehicle Data securely transmitted!")

if __name__ == "__main__":
    main()
