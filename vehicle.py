import socket
import json
import os
import time
import struct
import uuid
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Constants
HOST = '127.0.0.1'
PORT = 65432
CHALLENGE_SIZE = 32
MAX_MESSAGE_SIZE = 65536

def send_message(conn, data):
    conn.sendall(struct.pack("!I", len(data)) + data)

def receive_exact(conn, size):
    data = b""
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Connection closed while receiving data.")
        data += chunk
    return data

def receive_message(conn):
    length_data = receive_exact(conn, 4)
    message_length = struct.unpack("!I", length_data)[0]
    if message_length <= 0 or message_length > MAX_MESSAGE_SIZE:
        raise ValueError("Invalid message length received.")
    return receive_exact(conn, message_length)

def sign_data(private_key, data):
    return private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def verify_signature(public_key, signature, data):
    public_key.verify(
        signature,
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def serialize_ecdh_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def load_ecdh_public_key(data):
    return serialization.load_pem_public_key(data)

def derive_aes_key(private_key, peer_public_key, server_challenge, vehicle_challenge):
    shared_secret = private_key.exchange(ec.ECDH(), peer_public_key)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=server_challenge + vehicle_challenge,
        info=b"secure-v2i-ecdh-aes-gcm-session",
    ).derive(shared_secret)

def make_vehicle_ecdh_context(server_challenge, vehicle_challenge, vehicle_ecdh_public):
    return b"VEHICLE_ECDH" + server_challenge + vehicle_challenge + vehicle_ecdh_public

def make_server_ecdh_context(server_challenge, vehicle_challenge, vehicle_ecdh_public, server_ecdh_public):
    return b"SERVER_ECDH" + server_challenge + vehicle_challenge + vehicle_ecdh_public + server_ecdh_public

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
        server_challenge = receive_message(s)
        
        print("Signing Edge Server Challenge...")
        signature = sign_data(vehicle_private_key, server_challenge)
        print("Sending Challenge Signature back to Edge Server...")
        send_message(s, signature)

        print("Sending Vehicle Challenge to Edge Server...")
        vehicle_challenge = os.urandom(CHALLENGE_SIZE)
        send_message(s, vehicle_challenge)

        print("Verifying Edge Server Challenge Signature...")
        server_signature = receive_message(s)
        try:
            verify_signature(server_public_key, server_signature, vehicle_challenge)
            print("[SUCCESS] Edge Server Authentication Verified!")
        except Exception as e:
            print(f"[ERROR] Edge Server Authentication Failed! {e}")
            return
        
        # --- Phase 3: Ephemeral ECDH Key Agreement ---
        print("Generating ephemeral ECDH key pair...")
        vehicle_ecdh_private_key = ec.generate_private_key(ec.SECP256R1())
        vehicle_ecdh_public = serialize_ecdh_public_key(vehicle_ecdh_private_key.public_key())
        vehicle_ecdh_signature = sign_data(
            vehicle_private_key,
            make_vehicle_ecdh_context(server_challenge, vehicle_challenge, vehicle_ecdh_public)
        )
        vehicle_ecdh_package = {
            "public_key": vehicle_ecdh_public.decode("utf-8"),
            "signature": vehicle_ecdh_signature.hex()
        }

        print("Sending signed Vehicle ECDH Public Key...")
        send_message(s, json.dumps(vehicle_ecdh_package).encode("utf-8"))

        print("Receiving and verifying signed Edge Server ECDH Public Key...")
        server_ecdh_package = json.loads(receive_message(s).decode("utf-8"))
        server_ecdh_public = server_ecdh_package["public_key"].encode("utf-8")
        server_ecdh_signature = bytes.fromhex(server_ecdh_package["signature"])

        try:
            verify_signature(
                server_public_key,
                server_ecdh_signature,
                make_server_ecdh_context(server_challenge, vehicle_challenge, vehicle_ecdh_public, server_ecdh_public)
            )
            peer_ecdh_public_key = load_ecdh_public_key(server_ecdh_public)
            print("[SUCCESS] Edge Server ECDH Public Key Signature Verified!")
        except Exception as e:
            print(f"[ERROR] Edge Server ECDH Verification Failed! {e}")
            return

        aes_session_key = derive_aes_key(
            vehicle_ecdh_private_key,
            peer_ecdh_public_key,
            server_challenge,
            vehicle_challenge
        )
        print("[SUCCESS] AES Session Key derived with ephemeral ECDH!")
        
        # --- Phase 4: Secure State Dissemination ---
        print("Preparing Vehicle State Telemetry...")
        state_data = {
            "message_id": str(uuid.uuid4()),
            "vehicle_id": "V-4848",
            "position": {"x": 42.3601, "y": -71.0589},
            "velocity": 65.5,
            "qos_level": 2,
            "privacy_demand_psi": 0.85,
            "timestamp": time.time()
        }
        json_data = json.dumps(state_data).encode('utf-8')
        
        print("Signing Vehicle State payload (Non-repudiation)...")
        payload_signature = sign_data(vehicle_private_key, json_data)
        
        print("Encrypting Vehicle State payload with AES-GCM (Confidentiality & Integrity)...")
        aesgcm = AESGCM(aes_session_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, json_data, None)
        
        print("Sending Secure Package to Edge Server...")
        # Package structure: 12 bytes nonce + ciphertext (payload+mac) + 256 bytes signature
        secure_package = nonce + ciphertext + payload_signature
        send_message(s, secure_package)
        
        print("Vehicle Data securely transmitted!")

if __name__ == "__main__":
    main()
