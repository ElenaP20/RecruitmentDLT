from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Hash import SHA256
import base64
import json
#import ipfshttpclient

class Encryption:
    def __init__(self, cv_file, public_key_file):
        self.cv_file = cv_file
        self.public_key_file = public_key_file

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

    def encrypt_cv_data(self):
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

        with open("cv_packet.json", "w") as f:
            json.dump(cv_packet, f)

        # Create a separate file for the second part of the symmetric key
        with open("cv_symmetric_key_part2.json", "w") as f:
            json.dump({"SymmetricKeyPart2": base64.b64encode(encrypted_aes_key_part2).decode('utf-8')}, f)

        print("Packet with encrypted header and AES-encrypted CV content has been created successfully!")
        print("File with the second part of the symmetric key has been created.")
        
    # def upload_to_ipfs(self, files):
    #     client = ipfshttpclient.connect()  # Connect to IPFS daemon
    #     result = client.add(files)  # Upload files to IPFS

    #     # Return the IPFS link of the uploaded files
    #     return f"https://ipfs.io/ipfs/{result['Hash']}"


# Usage
cv_file = "CV.xml"  # Change to your CV file
public_key_file = "public_key.pem"

encryptor = Encryption(cv_file, public_key_file)
encryptor.encrypt_cv_data()

# # Upload the files to IPFS
# ipfs_link = encryptor.upload_to_ipfs(['cv_packet.json', 'cv_symmetric_key_part2.json'])
# print("IPFS Link for the bundle:", ipfs_link)
