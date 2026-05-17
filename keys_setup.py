import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_key_pair(name):
    # Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Generate RSA public key
    public_key = private_key.public_key()
    
    # Serialize private key to PEM
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key to PEM
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Save to files
    with open(f'{name}_private.pem', 'wb') as f:
        f.write(pem_private)
        
    with open(f'{name}_public.pem', 'wb') as f:
        f.write(pem_public)
        
    print(f"Generated {name} key pair.")

if __name__ == "__main__":
    print("Generating RSA key pairs for Vehicle and Edge Server...")
    # Ensure keys are generated in the current script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generate_key_pair('vehicle')
    generate_key_pair('edge_server')
    print("Setup complete. Keys are ready to be used.")
