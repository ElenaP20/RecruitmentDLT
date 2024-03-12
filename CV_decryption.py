from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64
import json
import re

from cv_parser import extract_cv_details

class KeyValuePairExtractor:
    def __init__(self):
        self.pattern = r'"([^"]+)"\s*:\s*"(.*?)"'
        self.second_pattern = r'secondhalf:\s*"([^"]+)"'
        self.extracted_values = {}  # Initialize extracted_values attribute

    def extract_key_value_pairs_from_text(self, text):
        matches = re.findall(self.pattern, text)
        second_matches = re.findall(self.second_pattern, text)
        
        for key, value in matches:
            self.extracted_values[key] = value
        
        for match in second_matches:
            self.extracted_values['secondhalf'] = match
        
        return matches
    
class FileProcessor:
    def __init__(self):
        self.key_value_extractor = KeyValuePairExtractor()

    def process_file_content(self, file_content):
        if isinstance(file_content, str):
            extracted_pairs = self.key_value_extractor.extract_key_value_pairs_from_text(file_content)

            print("Extracted key-value pairs:")
            for key, value in extracted_pairs:
                print(f"{key} -> {value}")
        else:
            print("Input is not a valid string.")

    def read_file_content(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    
    def download_file(self, content, file_path): 
        with open(file_path, 'w') as file:
            file.write(content)


class Decryption:
    def __init__(self, encrypted_cv_file, private_key_file):
        self.key_value_extractor = KeyValuePairExtractor()
        self.encrypted_cv_file = encrypted_cv_file
        self.private_key_file = private_key_file

    def load_private_key(self):
        with open(self.private_key_file, 'rb') as f:
            return RSA.import_key(f.read())

    def extract_values_from_json(self, json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
            return data

    def decrypt_half_key(self, encrypted_half, private_key):
        cipher_rsa = PKCS1_OAEP.new(private_key)
        try:
            return cipher_rsa.decrypt(base64.b64decode(encrypted_half))
        except ValueError as e:
            print(f"Error decrypting half key: {e}")
            return None

    def construct_symmetric_key(self, half_one, half_two):
        return half_one + half_two

    def decrypt_cv(self, symmetric_key, iv, encrypted_cv):
        cipher = AES.new(symmetric_key, AES.MODE_CBC, iv)
        decrypted_cv = cipher.decrypt(base64.b64decode(encrypted_cv))
        clean_cv = decrypted_cv.decode('utf-8').replace('\f', '')  # Remove form feed (U+000c)
        return clean_cv 

    def process(self):
        # Load encrypted CV details
        cv_details = self.extract_values_from_json(self.encrypted_cv_file)

        # Load additional key details
        key_details = self.extract_values_from_json('downloaded_file_2.json')

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

        print("Decrypted CV:")
        print(decrypted_cv)
        file_processor = FileProcessor() 
        file_processor.download_file(decrypted_cv, "decrypted_cv_1.xml")

if __name__ == "__main__":
# Usage
    decryption_instance = Decryption('downloaded_file_1.json', 'private_key.pem')
    decryption_instance.process()


# Assuming the decryption process correctly created 'decrypted_cv_1.xml'
    xml_file = 'decrypted_cv_1.xml'  
    cv_details = extract_cv_details(xml_file)
    print(cv_details)