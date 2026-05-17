import socket
import json
import os
import struct
import time
import threading
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Constants
HOST = '127.0.0.1'
PORT = 65432
CHALLENGE_SIZE = 32
RSA_SIGNATURE_SIZE = 256
MAX_MESSAGE_SIZE = 65536
REPLAY_DB_FILE = "used_message_ids.json"
replay_db_lock = threading.Lock()

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

def load_used_message_ids():
    if not os.path.exists(REPLAY_DB_FILE):
        return set()
    try:
        with open(REPLAY_DB_FILE, "r", encoding="utf-8") as replay_file:
            return set(json.load(replay_file))
    except (json.JSONDecodeError, OSError):
        return set()

def save_used_message_ids(message_ids):
    with open(REPLAY_DB_FILE, "w", encoding="utf-8") as replay_file:
        json.dump(sorted(message_ids), replay_file, indent=2)

def record_message_id_once(message_id):
    if not message_id:
        return False
    with replay_db_lock:
        used_message_ids = load_used_message_ids()
        if message_id in used_message_ids:
            return False
        used_message_ids.add(message_id)
        save_used_message_ids(used_message_ids)
        return True

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

def handle_vehicle(conn, addr, server_private_key, vehicle_public_key):
    with conn:
        print(f"Connected by Vehicle at {addr}")
        
        # --- Phase 2: Mutual Authentication (Challenge-Response) ---
        # 1. Edge Server challenges Vehicle
        server_challenge = os.urandom(CHALLENGE_SIZE)
        print(f"[{addr}] Sending Challenge to Vehicle...")
        send_message(conn, server_challenge)
        
        # 2. Receive and verify Vehicle's signed challenge
        signature = receive_message(conn)
        print(f"[{addr}] Received Challenge Signature from Vehicle. Verifying...")
        
        try:
            verify_signature(vehicle_public_key, signature, server_challenge)
            print(f"[{addr}] [SUCCESS] Vehicle Authentication Verified!")
        except Exception as e:
            print(f"[{addr}] [ERROR] Vehicle Authentication Failed! {e}")
            return

        # 3. Vehicle challenges Edge Server
        print(f"[{addr}] Waiting for Vehicle Challenge...")
        vehicle_challenge = receive_message(conn)
        print(f"[{addr}] Signing Vehicle Challenge to prove Edge Server identity...")
        server_signature = sign_data(server_private_key, vehicle_challenge)
        send_message(conn, server_signature)
        print(f"[{addr}] [SUCCESS] Edge Server Authentication Response Sent!")
            
        # --- Phase 3: Ephemeral ECDH Key Agreement ---
        print(f"[{addr}] Waiting for Vehicle ECDH Public Key...")
        ecdh_package = json.loads(receive_message(conn).decode("utf-8"))
        vehicle_ecdh_public = ecdh_package["public_key"].encode("utf-8")
        vehicle_ecdh_signature = bytes.fromhex(ecdh_package["signature"])

        try:
            verify_signature(
                vehicle_public_key,
                vehicle_ecdh_signature,
                make_vehicle_ecdh_context(server_challenge, vehicle_challenge, vehicle_ecdh_public)
            )
            peer_ecdh_public_key = load_ecdh_public_key(vehicle_ecdh_public)
            print(f"[{addr}] [SUCCESS] Vehicle ECDH Public Key Signature Verified!")
        except Exception as e:
            print(f"[{addr}] [ERROR] Vehicle ECDH Verification Failed! {e}")
            return

        server_ecdh_private_key = ec.generate_private_key(ec.SECP256R1())
        server_ecdh_public = serialize_ecdh_public_key(server_ecdh_private_key.public_key())
        server_ecdh_signature = sign_data(
            server_private_key,
            make_server_ecdh_context(server_challenge, vehicle_challenge, vehicle_ecdh_public, server_ecdh_public)
        )
        server_ecdh_package = {
            "public_key": server_ecdh_public.decode("utf-8"),
            "signature": server_ecdh_signature.hex()
        }
        send_message(conn, json.dumps(server_ecdh_package).encode("utf-8"))

        aes_session_key = derive_aes_key(
            server_ecdh_private_key,
            peer_ecdh_public_key,
            server_challenge,
            vehicle_challenge
        )
        print(f"[{addr}] [SUCCESS] AES Session Key derived with ephemeral ECDH!")
            
        # --- Phase 4: Secure State Dissemination ---
        print(f"[{addr}] Waiting for Secure State Payload...")
        # Protocol format: nonce (12 bytes) + ciphertext (includes tag) + signature (256 bytes)
        payload = receive_message(conn)
        if not payload:
            print(f"[{addr}] No payload received.")
            return
            
        nonce = payload[:12]
        signature = payload[-RSA_SIGNATURE_SIZE:]
        ciphertext = payload[12:-RSA_SIGNATURE_SIZE]
        
        print(f"[{addr}] Decrypting payload...")
        aesgcm = AESGCM(aes_session_key)
        try:
            decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            print(f"[{addr}] [ERROR] Failed to decrypt payload with AES key! {e}")
            return
            
        print(f"[{addr}] Verifying Payload Signature (Integrity & Non-repudiation)...")
        try:
            verify_signature(vehicle_public_key, signature, decrypted_data)
            print(f"[{addr}] [SUCCESS] Payload Signature Verified!")
        except Exception as e:
            print(f"[{addr}] [ERROR] Payload Signature Failed! {e}")
            return
            
        state_data = json.loads(decrypted_data.decode('utf-8'))
        if abs(time.time() - state_data.get("timestamp", 0)) > 60:
            print(f"[{addr}] [ERROR] Stale telemetry timestamp detected. Possible replay attack.")
            return

        if not record_message_id_once(state_data.get("message_id")):
            print(f"[{addr}] [ERROR] Duplicate or missing message_id detected. Possible replay attack.")
            return

        print(f"\n--- SECURE VEHICLE STATE RECEIVED FROM {addr} ---")
        print(json.dumps(state_data, indent=4))
        print("-------------------------------------")

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
        
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(
                target=handle_vehicle,
                args=(conn, addr, server_private_key, vehicle_public_key),
                daemon=True
            )
            client_thread.start()

if __name__ == "__main__":
    main()
