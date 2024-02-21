from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

# Generate the secret key
key = get_random_bytes(32)  # 256-bit key

# Create the AES cipher object (no IV needed for ECB mode)
aes_cipher = AES.new(key, AES.MODE_ECB)

# Read the XML file content
with open("CV.xml", "rb") as f:
    xml_data = f.read()

# Pad the data to a multiple of the block size
padded_data = pad(xml_data, AES.block_size)

# Encrypt the XML data using AES
aes_encrypted_data = aes_cipher.encrypt(padded_data)

# Read the recipient's RSA public key in PEM format
with open('recipient_public_key.pem', 'rb') as f:
    rsa_public_key_pem = f.read()

try:
    # Import the RSA public key from PEM format
    rsa_public_key = RSA.import_key(rsa_public_key_pem)
except ValueError as e:
    print("Error importing RSA public key:", e)
    print("Make sure the key format is supported and the file content is correct.")
    # Exit or handle the error accordingly
    exit(1)

# Create the RSA cipher object
rsa_cipher = PKCS1_v1_5.new(rsa_public_key)

# Encrypt the AES-encrypted data using RSA
rsa_encrypted_data = rsa_cipher.encrypt(aes_encrypted_data)

# Write the doubly encrypted data to a file
with open("doubly_encrypted_cv.dat", "wb") as f:
    f.write(rsa_encrypted_data)

print("XML file encrypted using AES-256 in ECB mode and then doubly encrypted with RSA successfully!")