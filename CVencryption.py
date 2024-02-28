from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64

# Read the XML file content
with open("CV.xml", "rb") as f:
    xml_data = f.read()

# Generate a random AES key
aes_key = get_random_bytes(32)  # 256-bit key

# Create AES cipher object
aes_cipher = AES.new(aes_key, AES.MODE_CBC)

# Pad the data to a multiple of the block size
padded_data = pad(xml_data, AES.block_size)

# Encrypt the XML data using AES
aes_encrypted_data = aes_cipher.encrypt(padded_data)

# Generate a random IV for AES
iv = aes_cipher.iv

# Read the recipient's RSA public key in PEM format
with open('test.pem', 'rb') as f:
    rsa_public_key_pem = f.read()

# Import the RSA public key from PEM format
rsa_public_key = RSA.import_key(rsa_public_key_pem)

# Create RSA cipher object
rsa_cipher = PKCS1_OAEP.new(rsa_public_key)

# Encrypt the CV data with AES
cv_encrypted_with_aes = aes_encrypted_data

# Split the AES key into two halves
half_aes_key_length = len(aes_key) // 2
encrypted_aes_key_part1 = rsa_cipher.encrypt(aes_key[:half_aes_key_length])
encrypted_aes_key_part2 = rsa_cipher.encrypt(aes_key[half_aes_key_length:])

# Write the packets to two separate files, each containing the iv and one half of the encrypted AES key in the header
with open("packet1.dat", "wb") as f1, open("packet2.dat", "wb") as f2:
    f1.write(iv + encrypted_aes_key_part1 + cv_encrypted_with_aes)
    f2.write(iv + encrypted_aes_key_part2 + cv_encrypted_with_aes)

print("Two packets with encrypted headers and AES-encrypted CV content have been created successfully!")
