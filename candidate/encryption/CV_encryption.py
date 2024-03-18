from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64
import json
import os

class Encryption:
    def __init__(self, cv_file, public_key_file, output_folder):
        self.cv_file = cv_file
        self.public_key_file = public_key_file
        self.output_folder = output_folder

    def read_cv_data(self):
        with open(self.cv_file, "rb") as f:
            return f.read()

    def generate_aes_key(self):
        return get_random_bytes(32)  # 256-bit key

    def generate_iv(self):
        return get_random_bytes(AES.block_size)  # Generate a random IV

    def encrypt_aes(self, cv_data, aes_key, iv):
        aes_cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        padded_data = pad(cv_data, AES.block_size)
        return aes_cipher.encrypt(padded_data)

    def read_rsa_public_key(self):
        with open(self.public_key_file, 'rb') as f:
            return RSA.import_key(f.read())

    def encrypt_with_rsa(self, data, rsa_public_key):
        rsa_cipher = PKCS1_OAEP.new(rsa_public_key)
        return rsa_cipher.encrypt(data)

    def encrypt_cv_data(self, cv_packet_file, symmetric_key_file):
        cv_data = self.read_cv_data()
        aes_key = self.generate_aes_key()
        iv = self.generate_iv()  # Generate IV
        aes_encrypted_cv = self.encrypt_aes(cv_data, aes_key, iv)
        rsa_public_key = self.read_rsa_public_key()
        encrypted_aes_key_part1 = self.encrypt_with_rsa(aes_key[:16], rsa_public_key)
        encrypted_aes_key_part2 = self.encrypt_with_rsa(aes_key[16:], rsa_public_key)

        # Constructing the CV packet with the specified format
        cv_packet = {
            "Header": {
                "IV": base64.b64encode(iv).decode('utf-8'),
                "HalfSymmetricKeyEncrypted": base64.b64encode(encrypted_aes_key_part1).decode('utf-8')
            },
            "Body": base64.b64encode(aes_encrypted_cv).decode('utf-8')
        }

        # Create the output folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # Writing the CV packet to the output folder
        cv_packet_file_path = os.path.join(self.output_folder, cv_packet_file)
        with open(cv_packet_file_path, "w") as f:
            json.dump(cv_packet, f)

        # Create a separate file for the second part of the symmetric key in the output folder
        symmetric_key_file_path = os.path.join(self.output_folder, symmetric_key_file)
        with open(symmetric_key_file_path, "w") as f:
            json.dump({"SymmetricKeyPart2": base64.b64encode(encrypted_aes_key_part2).decode('utf-8')}, f)

        print("Packet with encrypted header and AES-encrypted CV content has been created successfully!")
        print("File with the second part of the symmetric key has been created.")

if __name__ == "__main__":
    # Usage
    cv_file = input("Enter the path to your CV file: ")
    public_key_file = "public_key.pem"
    output_folder = "encrypted_CVs"
    cv_packet_file = input("Enter the name for the CV packet JSON file: ")
    symmetric_key_file = input("Enter the name for the symmetric key JSON file: ")

    encryptor = Encryption(cv_file, public_key_file, output_folder)
    encryptor.encrypt_cv_data(cv_packet_file, symmetric_key_file)
