import socket
import json
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Constants
HOST = '127.0.0.1'
PORT = 65432
CHALLENGE_SIZE = 32

def load_keys():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("edge_server_private.pem", "rb") as key_file:
        server_private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    with open("vehicle_public.pem", "rb") as key_file:
        vehicle_public_key = serialization.load_pem_public_key(
            key_file.read()
        )
    return server_private_key, vehicle_public_key

def main():
    print("Starting Edge Server...")
    try:
        server_private_key, vehicle_public_key = load_keys()
        print("Keys loaded successfully.")
    except Exception as e:
        print(f"Error loading keys. Have you run keys_setup.py? {e}")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Allow port reuse
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Edge Server listening on {HOST}:{PORT}")
        
        conn, addr = s.accept()
        with conn:
            print(f"Connected by Vehicle at {addr}")
            
            # --- Phase 2: Mutual Authentication (Challenge-Response) ---
            # 1. Edge Server generates Challenge
            challenge = os.urandom(CHALLENGE_SIZE)
            print("Sending Challenge to Vehicle...")
            conn.sendall(challenge)
            
            # 2. Receive Signature from Vehicle
            signature = conn.recv(256) # 2048-bit RSA signature is 256 bytes
            print("Received Challenge Signature from Vehicle. Verifying...")
            
            try:
                vehicle_public_key.verify(
                    signature,
                    challenge,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                print("[SUCCESS] Vehicle Authentication Verified!")
            except Exception as e:
                print(f"[ERROR] Vehicle Authentication Failed! {e}")
                return
                
            # --- Phase 3: Key Exchange (Session Key Reception) ---
            print("Waiting for Encrypted AES Session Key...")
            encrypted_session_key = conn.recv(256) # Encrypted with 2048-bit RSA
            
            try:
                aes_session_key = server_private_key.decrypt(
                    encrypted_session_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                print("[SUCCESS] AES Session Key successfully decrypted!")
            except Exception as e:
                print(f"[ERROR] Failed to decrypt AES Session Key! {e}")
                return
                
            # --- Phase 4: Secure State Dissemination ---
            print("Waiting for Secure State Payload...")
            # Protocol format: nonce (12 bytes) + ciphertext (includes tag) + signature (256 bytes)
            payload = conn.recv(4096)
            if not payload:
                print("No payload received.")
                return
                
            nonce = payload[:12]
            signature = payload[-256:]
            ciphertext = payload[12:-256]
            
            print("Decrypting payload...")
            aesgcm = AESGCM(aes_session_key)
            try:
                decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
            except Exception as e:
                print(f"[ERROR] Failed to decrypt payload with AES key! {e}")
                return
                
            print("Verifying Payload Signature (Integrity & Non-repudiation)...")
            try:
                vehicle_public_key.verify(
                    signature,
                    decrypted_data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                print("[SUCCESS] Payload Signature Verified!")
            except Exception as e:
                print(f"[ERROR] Payload Signature Failed! {e}")
                return
                
            state_data = json.loads(decrypted_data.decode('utf-8'))
            print("\n--- SECURE VEHICLE STATE RECEIVED ---")
            print(json.dumps(state_data, indent=4))
            print("-------------------------------------")

if __name__ == "__main__":
    main()
