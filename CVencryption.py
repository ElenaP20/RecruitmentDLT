from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# Generate the secret key
key = get_random_bytes(32)  # 256-bit key

# Create the cipher object (no IV needed for ECB mode)
cipher = AES.new(key, AES.MODE_ECB)

# Read the XML file content
with open("CV.xml", "rb") as f:
    xml_data = f.read()

# Pad the data to a multiple of the block size
padded_data = pad(xml_data, AES.block_size)

# Encrypt 
ciphertext = cipher.encrypt(padded_data)

# Write the encrypted data to a file
with open("encrypted_cv.xml", "wb") as f:
    f.write(ciphertext)

print("XML file encrypted using AES-256 in ECB mode successfully!")