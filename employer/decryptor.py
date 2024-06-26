from pathlib import Path
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
import base64
import json

# Class for decryption process
class Decryption:
    
    _downloaded_files = set()  # Class-level set to track downloaded files
    
    def __init__(self, encrypted_cv_file, second_half, private_key_file, file_processor):
        #self.key_value_extractor = KeyValuePairExtractor()
        self.encrypted_cv_file = encrypted_cv_file
        self.second_half = second_half
        self.private_key_file = private_key_file
        self.file_processor = file_processor  # Initialize FileProcessor instance

    def load_private_key(self):
        # Load private key from file
        with open(self.private_key_file, 'rb') as f:
            return load_pem_private_key(f.read(), password=None, backend=default_backend())

    def extract_values_from_json(self, json_file):
        # Extract values from JSON file
        with open(json_file, 'r') as f:
            data = json.load(f)
            return data

    def decrypt_half_key(self, encrypted_half, private_key):
        # Decrypt half of the symmetric key using RSA
        try:
            return private_key.decrypt(base64.b64decode(encrypted_half), asymmetric_padding.OAEP(
                mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
        except ValueError as e:
            print(f"Error decrypting half key: {e}")
            return None

    def construct_symmetric_key(self, half_one, half_two):
        # Combine two halves of the symmetric key
        return half_one + half_two

    def decrypt_cv(self, symmetric_key, iv, encrypted_cv):
        # Decrypt the CV using AES
        decryptor = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend()).decryptor()
        decrypted_cv = decryptor.update(base64.b64decode(encrypted_cv)) + decryptor.finalize()
        clean_cv = decrypted_cv.decode('utf-8').replace('\f', '')  # Remove form feed (U+000c)
        return clean_cv 

    def _generate_unique_file_name(self) -> str:
        # Generate a unique file name for the decrypted CV
        index = 1
        while True:
            file_name = f"decrypted_file_{index}.xml"
            if file_name not in Decryption._downloaded_files:
                return file_name
            index += 1
    
    def process(self):
        # Load encrypted CV details from the first half
        cv_details = self.extract_values_from_json(self.encrypted_cv_file)

        # Load additional key details from the second half of the key
        key_details = self.extract_values_from_json(self.second_half)

        # Load private key
        private_key = self.load_private_key()

        # Decrypt key components
        decrypted_half_one = self.decrypt_half_key(cv_details['Header']['HalfSymmetricKeyEncrypted'], private_key)
        decrypted_half_two = self.decrypt_half_key(key_details['SymmetricKeyPart2'], private_key)

        # Check if key components were decrypted correctly
        if decrypted_half_one is None or decrypted_half_two is None:
            print("Error: Could not decrypt all key components.")
            return

        # Construct the full symmetric key
        full_symmetric_key = self.construct_symmetric_key(decrypted_half_one, decrypted_half_two)

        # Decrypt the CV
        iv = base64.b64decode(cv_details['Header']['IV'])
        decrypted_cv = self.decrypt_cv(full_symmetric_key, iv, cv_details['Body'])

        # Generate a unique file name for the decrypted CV
        file_name = self._generate_unique_file_name()
        file_path = Path(file_name)

        # Download the decrypted CV
        self.file_processor.download_file(decrypted_cv, file_path)

        # Add downloaded file name to class-level set
        Decryption._downloaded_files.add(file_path.name)
        
        print("Decrypted CV can be found in the following file: ", file_path)
