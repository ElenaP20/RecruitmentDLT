import json
from ipfs_handler import IpfsHandle
from decryptor import Decryption
from file_processor import FileProcessor
from cv_parser import CVProcessor

# Define the file paths
ipfs_data_file = "ipfs_data.json"
private_key_file = "private_key.pem"

# Load IPFS data
with open(ipfs_data_file, 'r') as f:
    ipfs_data = json.load(f)

# Initialize IpfsHandler
ipfs_handler = IpfsHandle()

token_pairs = ipfs_handler.fetch_pairs_from_json(ipfs_data_file)
    
for index, (part_one, part_two) in enumerate(token_pairs, start=1):
    downloaded_file_path1, _ = ipfs_handler.get_file(part_one)
    downloaded_file_path2, _ = ipfs_handler.get_file(part_two)
        
    print(f"Pair {index}:")
    print(f"File downloaded at: {downloaded_file_path1}") 
    print(f"File downloaded at: {downloaded_file_path2}")
        
        # Initialize FileProcessor instances for each pair
    file_processor1 = FileProcessor()
        
        # Initialize Decryption instances for each pair
    decryption1 = Decryption(downloaded_file_path1, downloaded_file_path2, "private_key.pem", file_processor1)

        # Process decryption for the first pair of files
    decryption1.process()
        
        # Call CVProcessor to extract CV details from decrypted XML files
    xml_files = [f"decrypted_file_{index}.xml"]
        
        # Process CV details
    cv_processor = CVProcessor(xml_files)
    total_score = cv_processor.extract_total_score()

        # Update total scores in the original JSON file
    with open(ipfs_data_file, 'r') as f:
        original_data = json.load(f)

    for item in original_data['tokens']:
        if item['ipfsLink'] == part_one or item['secondPart'] == part_two:
            item['total_score'] = total_score

        # Write updated data back to JSON file
    with open(ipfs_data_file, 'w') as f:
        json.dump(original_data, f, indent=2)