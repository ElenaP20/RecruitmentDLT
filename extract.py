import re

def extract_key_value_pairs_from_text(text):
    pattern = r'"([^"]+)"\s*:\s*"(.*?)"'
    matches = re.findall(pattern, text)
    
    # New pattern for secondhalf: "second"
    second_pattern = r'secondhalf:\s*"([^"]+)"'
    second_matches = re.findall(second_pattern, text)
    
    for match in second_matches:
        matches.append(('secondhalf', match))
    
    return matches

def process_file_content(file_content):
    if isinstance(file_content, str):
        extracted_pairs = extract_key_value_pairs_from_text(file_content)

        print("Extracted key-value pairs:")
        for key, value in extracted_pairs:
            print(f"{key} -> {value}")
    else:
        print("Input is not a valid string.")

# Function to read content from a file
def read_file_content(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

# Example file path
file_path1 = 'downloaded_file_1.json'

# Read content from the file
file_content1 = read_file_content(file_path1)

# Process the file content
process_file_content(file_content1)

# Example file path
file_path2 = 'downloaded_file_2.json'

# Read content from the file
file_content2 = read_file_content(file_path2)

# Process the file content
process_file_content(file_content2)