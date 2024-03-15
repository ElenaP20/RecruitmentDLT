from key_value_extractor import KeyValuePairExtractor
import re

class FileProcessor:
    def __init__(self):
        self.key_value_extractor = KeyValuePairExtractor()
        self._downloaded_files = set()  # Initialize set to track downloaded files

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
        # Remove non-printable characters, including form feed characters
        cleaned_content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        with open(file_path, 'w') as file:
            file.write(cleaned_content)
        self._downloaded_files.add(file_path.name)  # Add downloaded file name to set
