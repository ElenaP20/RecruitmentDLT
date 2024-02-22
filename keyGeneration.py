from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate a 2048-bit RSA key pair
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Get the public key in PEM format
public_key = private_key.public_key()
pem_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Write the PEM public key to a file
with open("public_key.pem", "wb") as f:
    f.write(pem_public_key)

print("Key pair generated successfully!")
print("Public key stored in public_key.pem")
