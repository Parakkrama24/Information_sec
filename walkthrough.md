# Secure V2I Communication - Walkthrough

The Secure Vehicle-to-Edge Communication protocol has been successfully implemented and tested! 

This project perfectly fulfills the requirements of your Information Security module while seamlessly adapting to your "GARFL" Final Year Project architecture.

## What Was Accomplished
We created a Python project inside `e:\7th Sem\EC7201 - Information Security\Project\Secure_V2I_Communication`. The project contains a fully operational protocol that authenticates a vehicle and securely transmits its telemetry (position, QoS, and privacy demand) to an Edge Server.

Here is what we implemented:

### 1. `keys_setup.py`
This script uses the `cryptography` library to generate standard 2048-bit RSA Private and Public keys for both the Vehicle and the Edge Server. This simulates a pre-shared key setup or a simple Public Key Infrastructure (PKI), serving as the foundation of trust.

### 2. `edge_server.py`
The edge server script simulates the Cluster Head in your FYP. It acts as a TCP server that:
- Issues cryptographic challenges (nonces) to incoming vehicle connections.
- Verifies the vehicle's RSA signature to authenticate it.
- Decrypts the incoming AES Session Key using its RSA Private Key.
- Authenticates and decrypts the final secure telemetry payload.

### 3. `vehicle.py`
The vehicle script connects to the Edge Server and performs the client side of the protocol:
- Signs the Edge Server's challenge to prove its identity (Authentication).
- Generates a random 256-bit AES Session Key and securely encrypts it using the Edge Server's RSA Public Key (Key Exchange).
- Encrypts its JSON telemetry state using the AES Session Key and digitally signs it to prevent tampering (Confidentiality, Integrity, and Non-repudiation).

## Execution Results

We successfully created and activated a virtual environment (`venv`), installed the `cryptography` dependency, generated the keys, and ran the two scripts.

**Edge Server Output Logs:**
```text
Starting Edge Server...
Keys loaded successfully.
Edge Server listening on 127.0.0.1:65432
Connected by Vehicle at ('127.0.0.1', 10665)
Sending Challenge to Vehicle...
Received Challenge Signature from Vehicle. Verifying...
[SUCCESS] Vehicle Authentication Verified!
Waiting for Encrypted AES Session Key...
[SUCCESS] AES Session Key successfully decrypted!
Waiting for Secure State Payload...
Decrypting payload...
Verifying Payload Signature (Integrity & Non-repudiation)...
[SUCCESS] Payload Signature Verified!

--- SECURE VEHICLE STATE RECEIVED ---
{
    "vehicle_id": "V-4848",
    "position": {
        "x": 42.3601,
        "y": -71.0589
    },
    "velocity": 65.5,
    "qos_level": 2,
    "privacy_demand_psi": 0.85
}
-------------------------------------
```

## How to Present This for Your Exam/Viva
For your evaluation:
1. Open two separate command prompt windows and activate the virtual environment in both (`.\venv\Scripts\activate`).
2. Run `python edge_server.py` in the first window.
3. Run `python vehicle.py` in the second window.
4. Explain the protocol phases (Challenge-Response $\rightarrow$ RSA Key Exchange $\rightarrow$ AES-GCM Encrypted Payload) sequentially as the logs appear on the screen.

> [!TIP]
> This effectively checks off all requirements on your project rubric: **Untrusted Entities** (Vehicle and Edge), **CIA** (AES-GCM encryption), and **Authentication/Non-repudiation** (RSA Signatures and Challenge-Response).
