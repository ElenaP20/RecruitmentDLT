# importing necessary libraries
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import base64
import json
import os

class Encryption:
    
    # initializing the encryption object with the CV file, public key file, and output folder
    def __init__(self, cv_file, public_key_file, output_folder):
        self.cv_file = cv_file
        self.public_key_file = public_key_file
        self.output_folder = output_folder

    # reading the data from the CV file
    def read_cv_data(self):
        with open(self.cv_file, "rb") as f:
            return f.read()

    # generating a random AES key (256-bit)
    def generate_aes_key(self):
        return os.urandom(32)  # 256-bit key

    # generating a random initialization vector (IV)
    def generate_iv(self):
        return os.urandom(16) 

    # encrypting the CV data using AES encryption with CBC mode
    def encrypt_aes(self, cv_data, aes_key, iv):
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(cv_data) + padder.finalize()
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(padded_data) + encryptor.finalize()

    # reading the RSA public key from the specified file
    def read_rsa_public_key(self):
        with open(self.public_key_file, 'rb') as f:
            return serialization.load_pem_public_key(f.read(), backend=default_backend())

    # encrypting data using RSA encryption with OAEP padding
    def encrypt_with_rsa(self, data, rsa_public_key):
        return rsa_public_key.encrypt(
            data,
            asymmetric_padding.OAEP(
                mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def encrypt_cv_data(self, cv_packet_file, symmetric_key_file):
        try:
            if not os.path.isfile(self.cv_file):
                print("Error: CV file not found.")
                exit()
            if not self.cv_file.endswith('.xml'):
                print("Error: CV file should be an XML.")
                exit()
            if not cv_packet_file.endswith('.json'):
                print("Error: CV packet file should be a JSON.")
                exit()
            if not symmetric_key_file.endswith('.json'):
                print("Error: Symmetric key file should be a JSON.")
                exit()
                
            # reading CV data
            cv_data = self.read_cv_data()
            
            # generating AES key and IV
            aes_key = self.generate_aes_key()
            iv = self.generate_iv()  
            
            # encrypting CV data using AES
            aes_encrypted_cv = self.encrypt_aes(cv_data, aes_key, iv)
            
            # reading RSA public key
            rsa_public_key = self.read_rsa_public_key()
            
            # splitting the encrypted key into two parts and encrypting them with RSA
            encrypted_aes_key_part1 = self.encrypt_with_rsa(aes_key[:16], rsa_public_key)
            encrypted_aes_key_part2 = self.encrypt_with_rsa(aes_key[16:], rsa_public_key)

            # constructing the CV packet with encrypted header and AES-encrypted CV content
            cv_packet = {
                "Header": {
                    "IV": base64.b64encode(iv).decode('utf-8'),
                    "HalfSymmetricKeyEncrypted": base64.b64encode(encrypted_aes_key_part1).decode('utf-8')
                },
                "Body": base64.b64encode(aes_encrypted_cv).decode('utf-8')
            }

            # creating the output folder if it doesn't exist
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)

            # writing the CV packet to the output folder
            cv_packet_file_path = os.path.join(self.output_folder, cv_packet_file)
            with open(cv_packet_file_path, "w") as f:
                json.dump(cv_packet, f)

            # creating a separate file for the second part of the symmetric key in the output folder
            symmetric_key_file_path = os.path.join(self.output_folder, symmetric_key_file)
            with open(symmetric_key_file_path, "w") as f:
                json.dump({"SymmetricKeyPart2": base64.b64encode(encrypted_aes_key_part2).decode('utf-8')}, f)

            # printing success messages
            print("Packet with encrypted header and AES-encrypted CV content has been created successfully!")
            print("File with the second part of the symmetric key has been created.")
            
        except FileNotFoundError:
            print("Error: File not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    # usage
    # user entering the CV file path, CV packet file name, and symmetric key file name
    cv_file = input("Enter the path to your CV file: ")
    cv_packet_file = input("Enter the name for the CV packet JSON file: ")
    symmetric_key_file = input("Enter the name for the symmetric key JSON file: ")
    
    # specifying the public key file and output folder
    public_key_file = "public_key.pem"
    output_folder = "encrypted_CVs"

    # encrypting the CV data and generate CV packet and symmetric key files
    encryptor = Encryption(cv_file, public_key_file, output_folder)
    encryptor.encrypt_cv_data(cv_packet_file, symmetric_key_file)
