from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64

class Encryption:
    def __init__(self, xml_file, public_key_file):
        self.xml_file = xml_file
        self.public_key_file = public_key_file

    def read_xml_data(self):
        with open(self.xml_file, "rb") as f:
            return f.read()

    def generate_aes_key(self):
        return get_random_bytes(32)  # 256-bit key

    def encrypt_aes(self, xml_data, aes_key):
        aes_cipher = AES.new(aes_key, AES.MODE_CBC)
        padded_data = pad(xml_data, AES.block_size)
        return aes_cipher.encrypt(padded_data), aes_cipher.iv

    def read_rsa_public_key(self):
        with open(self.public_key_file, 'rb') as f:
            return RSA.import_key(f.read())

    def encrypt_with_rsa(self, data, rsa_public_key):
        rsa_cipher = PKCS1_OAEP.new(rsa_public_key)
        return rsa_cipher.encrypt(data)

    def encrypt_data(self):
        xml_data = self.read_xml_data()
        aes_key = self.generate_aes_key()
        aes_encrypted_data, iv = self.encrypt_aes(xml_data, aes_key)
        rsa_public_key = self.read_rsa_public_key()
        encrypted_aes_key_part1 = self.encrypt_with_rsa(aes_key[:16], rsa_public_key)
        encrypted_aes_key_part2 = self.encrypt_with_rsa(aes_key[16:], rsa_public_key)

        with open("packet1.dat", "wb") as f1, open("packet2.dat", "wb") as f2:
            f1.write(iv + encrypted_aes_key_part1 + aes_encrypted_data)
            f2.write(iv + encrypted_aes_key_part2 + aes_encrypted_data)

        print("Two packets with encrypted headers and AES-encrypted CV content have been created successfully!")

# Usage
encryptor = Encryption("CV.xml", "test.pem")
encryptor.encrypt_data()
