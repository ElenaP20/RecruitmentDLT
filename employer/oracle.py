# importing necessary libraries and modules
import time
from web3 import Web3
import json
import sys
from decryptor import Decryption
from file_processor import FileProcessor
from cv_parser import CVProcessor
from pathlib import Path  # Added Path import
from contract_wrapper import ContractWrapper

parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)
from ipfs_handler import IpfsHandle

# Define a function to handle the ExecutionTime event
def handle_execution_time(event):
    # Extract the execution time from the event
    execution_time = event['args']['time']
    print("Execution time:", execution_time, "seconds")
    
# Defining Oracle class for interacting with the Ethereum contract and handling events
class Oracle:
    
    def __init__(self, contract_address, private_key):
        
        # Initializing Web3 instance with a connection to the local Ethereum node (using Ganache RPC)
        self.web3 = Web3(Web3.HTTPProvider('http://localhost:7542'))
        
        # Initializing ContractWrapper instance for interacting with the Ethereum contract
        self.contract_wrapper = ContractWrapper(contract_address, private_key)
        
        # Initializing FileProcessor instance for file processing
        self.file_processor = FileProcessor()  
        self.files_to_delete = []
            
    # Fetching all IPFS links from the Ethereum contract
    def get_all_ipfs_links(self):
        try:
            # getting all IPFS links for a specific advert ID (111; 222; 333)
            result = self.contract_wrapper.fetch_links(111)
            if result:
                
                # Writing IPFS links to a JSON file
                with open('ipfs_data.json', 'w') as json_file:
                    json.dump(result, json_file, indent=2)
                print("Data written to ipfs_data.json successfully.")
                print("Evaluation has started...")
                
                # Processing tokens and the IPFS links for each token
                self.process_tokens()
        except Exception as e:
            print("Error fetching IPFS links:", e)

    # Processing tokens fetched from the Ethereum contract
    def process_tokens(self):
        try:
            # Reading data from the JSON file containing IPFS links
            data = self.contract_wrapper.read_json_data('ipfs_data.json')
            if data:
                xml_files_list = []
                for index, token in enumerate(data.get('tokens', []), start=1):
                    start_time = time.time()  # Start time measurement for each token
                    # Extracting token details
                    token_id = token.get('tokenId')
                    ipfs_link = token.get('ipfsLink')
                    second_part = token.get('secondPart')
                    
                    # Initializing IpfsHandle instance for handling IPFS interactions
                    handler = IpfsHandle()
                    
                    # Downloading files from IPFS
                    downloaded_file_path1, _ = handler.get_file(ipfs_link)
                    downloaded_file_path2, _ = handler.get_file(second_part)
                    self.files_to_delete.append(downloaded_file_path1)
                    self.files_to_delete.append(downloaded_file_path2)
                    
                    # Initializing Decryption instance for decrypting files
                    decryption = Decryption(downloaded_file_path1, downloaded_file_path2, "private_key.pem", self.file_processor) 
                    decryption.process()
                    
                    # Processing decrypted files
                    xml_files = f"decrypted_file_{index}.xml"
                    xml_files_list.append(xml_files)
                    cv_processor = CVProcessor([xml_files], 'ipfs_data.json')
                    total_score = cv_processor.extract_cv_details()
                    try:
                        # Sending the token details to the Ethereum contract and returning the transaction hash
                        tx_hash = self.contract_wrapper.send_score(
                            token_id, ipfs_link, second_part, total_score
                        )
                    except Exception as e:
                        print(f"Error processing token {token_id}: {e}")
                            
                    # Delete the downloaded and decrypted files after processing
                    self.files_to_delete.extend(xml_files_list)
                    self.delete_files()                
                    
                    end_time = time.time()  # End time measurement for each token
                    execution_time = end_time - start_time
                    print(f"Execution time for token {token_id}: {execution_time} seconds")
                    print(f"Evaluation completed for token {token_id}!")
                    
            self.empty_data_file()
            # Print completion message
            print("All tokens processed successfully.")
        except Exception as e:
            print("Error processing tokens:", e)
                    
    def delete_files(self):
        try:
            for file_path in self.files_to_delete:
                if isinstance(file_path, list):  # Check if file_path is a list
                    for file in file_path:
                        if Path(file).exists():
                            Path(file).unlink()
                else:
                    if Path(file_path).exists():
                        Path(file_path).unlink()
            
            #print("All files deleted successfully.")
        except Exception as e:
            print("Error deleting files:", e)
    
    def empty_data_file(self):
        try:
            # Check if ipfs_data.json file exists before emptying it
            ipfs_data_file_path = 'ipfs_data.json'
            if Path(ipfs_data_file_path).exists():
                # Open the ipfs_data.json file in write mode and write an empty JSON object
                with open(ipfs_data_file_path, 'w') as json_file:
                    json.dump({}, json_file)
                print("ipfs_data.json file emptied successfully.")
            else:
                print("ipfs_data.json file does not exist.")

            # Check if combined_data.json file exists before emptying it
            combined_data_file_path = 'combined_data.json'
            if Path(combined_data_file_path).exists():
                # Empty the combined_data.json file
                with open(combined_data_file_path, 'w') as combined_file:
                    json.dump({}, combined_file)
                print("combined_data.json file emptied successfully.")
            else:
                print("combined_data.json file does not exist.")

        except Exception as e:
            print("Error emptying ipfs_data.json and combined_data.json files:", e)
  
    # Evaluating events emitted by the Ethereum contract
    def audit(self, event):
        
        # Retrieving the arguments from the event
        _tokenId = event['args']['_tokenId']
        link1 = event['args']['ipfsLink1']
        link2 = event['args']['ipfsLink2']
        score = event['args']['totalScore']
        print("TokenId:", _tokenId)
        print("IPFS Link 1:", link1)
        print("IPFS Link 2:", link2)
        print("Total Score:", score)
        print("Evaluation started...")
        
        # Combining the IPFS links into a JSON file
        combined_data = {"ipfsLink1": link1, "ipfsLink2": link2}
        with open('combined_data.json', 'w') as json_file:
            json.dump(combined_data, json_file)
            
        # Processing the evaluation using the fetched data
        self.process_audit(_tokenId, link1, link2, score, 'combined_data.json')

    # Processing evaluation based on emitted events
    def process_audit(self, token_id, ipfs_link, second_part, score, ipfs_file):
        
        # Handling IPFS interactions
        handler = IpfsHandle()
        
        # Downloading files from IPFS
        downloaded_file_path1, _ = handler.get_file(ipfs_link)
        downloaded_file_path2, _ = handler.get_file(second_part)
        
        self.files_to_delete.append(downloaded_file_path1)
        self.files_to_delete.append(downloaded_file_path2)
        
        # Initializing Decryption instance for decrypting files
        decryption = Decryption(downloaded_file_path1, downloaded_file_path2, "private_key.pem", self.file_processor)
        decryption.process()
        
        # Processing decrypted files
        xml_files = [f"decrypted_file_1.xml"]
        cv_processor = CVProcessor(xml_files, ipfs_file)
        total_score = cv_processor.extract_cv_details()
        try:
            # Sending the token details to the Ethereum contract and returning the transaction hash
            tx_hash = self.contract_wrapper.send_score(
            token_id, ipfs_link, second_part, total_score
            )
        except Exception as e:
            print(f"Error processing token {token_id}: {e}")
              
        self.files_to_delete.extend(xml_files)
        self.delete_files() 
        print(f"Evaluation completed for token {token_id}!")
        self.empty_data_file()

    # Listening for events emitted by the Ethereum contract
    def listen_for_events(self):
        
        # Filtering events emitted by the contract
        event_filter = self.contract_wrapper.get_event_filter()
        while True:
            try:
                # Getting new event entries from the event filter
                logs = event_filter.get_new_entries()
                
                # Iterating through each new event entry
                for log in logs:
                    
                    # Evaluating the event
                    self.audit(log)
                    
            # Handle keyboard interrupt to exit the event listener
            except KeyboardInterrupt:
                print("Exiting event listener.")
                break
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    #defining contract address and private key (key taken from Ganache)
    contract_address = '0x79E5e3A5E9F35724dc2eBa917A2312C6b8050691'
    private_key = '0xa5b94567be428698d8b6e622feed9c79e1770d6100179b707d810bbd8d87abf8'
    
    #initializing the oracle instance
    oracle = Oracle(contract_address, private_key)
    #print("Current address:", oracle.web3.eth.accounts[0])
    
    #fetching all IPFS links and listening for events (for audit purpose)
    oracle.get_all_ipfs_links()
    #oracle.listen_for_events()