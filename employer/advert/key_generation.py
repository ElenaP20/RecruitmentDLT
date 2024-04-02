from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

#https://github.com/felipevalentin/Crypto-Tools/blob/main/crypto.py

# Generate a 2048-bit RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Serialize the private key to PEM format
private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

# Write the private key to a file
with open("private_key.pem", "wb") as f:
    f.write(private_key_pem)
print("Private key stored in private_key.pem")

# Extract the public key
public_key = private_key.public_key()

# Serialize the public key to PEM format
public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Write the public key to a file
with open("public_key.pem", "wb") as f:
    f.write(public_key_pem)
    
print("Public key stored in public_key.pem")
