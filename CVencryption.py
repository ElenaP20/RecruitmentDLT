from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Hash import SHA256
import base64
import json
import requests

class Encryption:
    def __init__(self, cv_file, public_key_file, nft_storage_api_key):
        self.cv_file = cv_file
        self.public_key_file = public_key_file
        self.nft_storage_api_key = nft_storage_api_key

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
        
    def upload_to_nft_storage(self, files):
        ipfs_links = {}

        for file in files:
            # Read the file content
            with open(file, "rb") as f:
                file_content = f.read()

            # Set up headers with the API key
            headers = {
                "Authorization": f"Bearer {self.nft_storage_api_key}"
            }

            # Upload file to NFT.storage
            response = requests.post("https://api.nft.storage/upload", files={"file": file_content}, headers=headers)
            ipfs_link = response.json()["value"]["cid"]
            ipfs_links[file] = f"https://cf-ipfs.com/ipfs/{ipfs_link}"

        return ipfs_links

# Usage
cv_file = "CV.xml"  # Change to your CV file
public_key_file = "public_key.pem"
nft_storage_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweGZCMGQ3RDQ2MkU0RkQ2NUQ2NjY1MTI0OTgzYTFjOWQ3MTk0YkNGNzIiLCJpc3MiOiJuZnQtc3RvcmFnZSIsImlhdCI6MTcxMDA4ODMzNzYxOSwibmFtZSI6IlJlY3J1aXRtZW50In0.6rVcafYK6-w6W7yIQQTgPBbYKDX7t4s6aJjgnTXHwL4"

encryptor = Encryption(cv_file, public_key_file, nft_storage_api_key)
encryptor.encrypt_cv_data()

# Upload the files to NFT.storage
ipfs_links = encryptor.upload_to_nft_storage(['cv_packet.json', 'cv_symmetric_key_part2.json'])
for file, link in ipfs_links.items():
    print(f"IPFS Link for {file}: {link}")