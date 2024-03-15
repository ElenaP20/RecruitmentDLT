import re
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
  