# Secure V2I Communication

Secure V2I Communication is a Python proof of concept for secure vehicle-to-infrastructure messaging. It demonstrates mutual authentication, ephemeral ECDH session key agreement, AES-GCM encrypted telemetry, RSA-PSS signatures, and basic replay protection.

## Project Structure

- `Secure_V2I_Communication/keys_setup.py` generates RSA key pairs for the vehicle and edge server.
- `Secure_V2I_Communication/edge_server.py` runs the edge server on `127.0.0.1:65432`.
- `Secure_V2I_Communication/vehicle.py` connects as the vehicle client and sends signed, encrypted telemetry.
- `Secure_V2I_Communication/requirements.txt` lists the Python dependency.

## Requirements

- Python 3.10 or newer
- `cryptography`

Install dependencies:

```powershell
cd Secure_V2I_Communication
python -m pip install -r requirements.txt
```

## Run

Generate the RSA key pairs:

```powershell
python keys_setup.py
```

Start the edge server in one terminal:

```powershell
python edge_server.py
```

Run the vehicle client in another terminal:

```powershell
python vehicle.py
```

The edge server will verify the vehicle identity, complete an authenticated ECDH key exchange, decrypt the telemetry payload, verify the payload signature, and reject duplicate or stale messages.

## Notes

- Runtime replay state is stored in `used_message_ids.json`.
- The demo uses localhost networking and is intended for learning and testing.
- Private key files are generated without passwords, so handle them carefully outside a demo environment.
