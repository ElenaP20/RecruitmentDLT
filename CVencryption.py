from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64

# References
# - pycryptodome: https://pypi.org/project/pycryptodome/
# - AES: https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
# - CBC mode: https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Cipher_Block_Chaining_(CBC)
# - RSA: https://en.wikipedia.org/wiki/RSA_(cryptosystem)
# - OAEP padding: https://en.wikipedia.org/wiki/Optimal_Asymmetric_Encryption_Padding

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
with open('public_key.pem', 'rb') as f:
    rsa_public_key_pem = f.read()

# Import the RSA public key from PEM format
rsa_public_key = RSA.import_key(rsa_public_key_pem)

# Create RSA cipher object
rsa_cipher = PKCS1_OAEP.new(rsa_public_key)

# Encrypt the AES key with RSA
encrypted_aes_key = rsa_cipher.encrypt(aes_key)

# Split the AES key into two halves
half_aes_key_length = len(aes_key) // 2
encrypted_aes_key_part1 = encrypted_aes_key[:half_aes_key_length]
encrypted_aes_key_part2 = encrypted_aes_key[half_aes_key_length:]

# Prepare the packet: header (encrypted half of AES key) + body (IV + AES-encrypted data)
packet = encrypted_aes_key_part1 + encrypted_aes_key_part2 + iv + aes_encrypted_data

# Write the packet to a file
with open("encrypted_cv_packet.dat", "wb") as f:
    f.write(packet)

print("Encrypted CV data exported as a packet successfully!")