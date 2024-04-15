from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

#https://github.com/felipevalentin/Crypto-Tools/blob/main/crypto.py
class KeyGenerator:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_key_pair(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def save_keys(self):
        if not self.private_key:
            print("Error: No key pair generated. Call generate_key_pair first.")
            return
        print("To avoid overriding the private key stored on the employer's side, do not name the files private_key.pem or public_key.pem")
        private_key_filename = input("Enter a filename for your private key (include .pem): ")
        public_key_filename = input("Enter a filename for your public key (include .pem): ")

        # Serialize and save the private key
        private_key_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(private_key_filename, "wb") as f:
            f.write(private_key_pem)

        # Serialize and save the public key
        public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(public_key_filename, "wb") as f:
            f.write(public_key_pem)

        print(f"Private key stored in {private_key_filename}")
        print(f"Public key stored in {public_key_filename}")

if __name__ == "__main__":
    generator = KeyGenerator()
    generator.generate_key_pair()
    generator.save_keys()