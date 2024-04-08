#importing necessary libraries and modules
import time
from web3 import Web3
import json
from ipfs_handler import IpfsHandle
from decryptor import Decryption
from file_processor import FileProcessor
from cv_parser import CVProcessor
from pathlib import Path
from contract_wrapper import ContractWrapper

# Define a function to handle the ExecutionTime event
def handle_execution_time(event):
    # Extract the execution time from the event
    execution_time = event['args']['time']
    print("Execution time:", execution_time, "seconds")
    
#defining Oracle class for interacting with the Ethereum contract and handling events
class Oracle:
    
    def __init__(self, contract_address, private_key):
        
        #initializing Web3 instance with a connection to the local Ethereum node (using Ganache RPC)
        self.web3 = Web3(Web3.HTTPProvider('http://localhost:7547'))
        
        #initializing ContractWrapper instance for interacting with the Ethereum contract
        self.contract_wrapper = ContractWrapper(contract_address, private_key)
        
        #initializing FileProcessor instance for file processing
        self.file_processor = FileProcessor()  
            
    #fetching all IPFS links from the Ethereum contract
    def get_all_ipfs_links(self):
        try:
            #calling the contract wrapper to get all IPFS links for a specififc advert ID (111; 222; 333; etc)
            result = self.contract_wrapper.get_all_ipfs_links(111)
            if result:
                
                #writing IPFS links to a JSON file
                with open('ipfs_data.json', 'w') as json_file:
                    json.dump(result, json_file, indent=2)
                print("Data written to ipfs_data.json successfully.")
                print("Evaluation has started...")
                
                #processing tokens and the ipfs links for each token
                self.process_tokens()
        except Exception as e:
            print("Error fetching IPFS links:", e)

    #processing tokens fetched from the Ethereum contract
    def process_tokens(self):
        
        #reading data from the JSON file containing IPFS links
        data = self.contract_wrapper.read_json_data('ipfs_data.json')
        if data:
            for index, token in enumerate(data.get('tokens', []), start=1):
                start_time = time.time()  # Start time measurement for each token
                #extracting token details
                token_id = token.get('tokenId')
                ipfs_link = token.get('ipfsLink')
                second_part = token.get('secondPart')
                
                #initializing IpfsHandle instance for handling IPFS interactions
                handler = IpfsHandle()
                
                #downloading files from IPFS
                downloaded_file_path1, _ = handler.get_file(ipfs_link)
                downloaded_file_path2, _ = handler.get_file(second_part)
                
                #initializing Decryption instance for decrypting files
                decryption = Decryption(downloaded_file_path1, downloaded_file_path2, "private_key.pem", self.file_processor) 
                decryption.process()
                
                #processing decrypted files
                xml_files = [f"decrypted_file_{index}.xml"]
                cv_processor = CVProcessor(xml_files, 'ipfs_data.json')
                total_score = cv_processor.extract_cv_details()
                try:
                    # Estimate gas cost
                    gas_estimate = self.contract_wrapper.estimate_gas(token_id, ipfs_link, second_part, total_score)
                    print(f"Gas estimate for token {token_id}: {gas_estimate}")

                    # Sending the token details to the Ethereum contract
                    tx_hash = self.contract_wrapper.process_token(token_id, ipfs_link, second_part, total_score, gas=gas_estimate)
                    receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

                    # Get the block number of the transaction
                    tx_block_number = receipt['blockNumber']

                    # Get the current block number
                    current_block_number = self.web3.eth.blockNumber

                    # Calculate the number of confirmations
                    confirmations = current_block_number - tx_block_number

                    print(f"Transaction for token {token_id} has {confirmations} confirmations.")

                except Exception as e:
                    print(f"Error processing token {token_id}: {e}")
                
                # Delete the decrypted files after processing
                self.delete_decrypted_files()
                
                end_time = time.time()  # End time measurement for each token
                execution_time = end_time - start_time
                print(f"Execution time for token {token_id}: {execution_time} seconds")
                
    def delete_decrypted_files(self):
        try:
            decrypted_files = Path().glob("decrypted_file_*.xml")
            for file in decrypted_files:
                file.unlink()
            print("Decrypted files deleted successfully.")
        except Exception as e:
            print("Error deleting decrypted files:", e)
            
    #evaluating events emitted by the Ethereum contract
    def evaluate(self, event):
        
        #retrieving the arguments from the event
        _tokenId = event['args']['_tokenId']
        link1 = event['args']['ipfsLink1']
        link2 = event['args']['ipfsLink2']
        score = event['args']['totalScore']
        print("TokenId:", _tokenId)
        print("IPFS Link 1:", link1)
        print("IPFS Link 2:", link2)
        print("Total Score:", score)
        print("Evaluation started...")
        
        #combining the IPFS links into a JSON file
        combined_data = {"ipfsLink1": link1, "ipfsLink2": link2}
        with open('combined_data.json', 'w') as json_file:
            json.dump(combined_data, json_file)
            
        #processing the evaluation using the fetched data
        self.process_evaluation(_tokenId, link1, link2, score, 'combined_data.json')

    #processing evaluation based on emitted events
    def process_evaluation(self, token_id, ipfs_link, second_part, score, ipfs_file):
        
        #handling IPFS interactions
        handler = IpfsHandle()
        
        #downloading files from IPFS
        downloaded_file_path1, _ = handler.get_file(ipfs_link)
        downloaded_file_path2, _ = handler.get_file(second_part)
        
        #initializing Decryption instance for decrypting files
        decryption = Decryption(downloaded_file_path1, downloaded_file_path2, "private_key.pem")
        decryption.process()
        
        #processing decrypted files
        xml_files = [f"decrypted_file_1.xml"]
        cv_processor = CVProcessor(xml_files, ipfs_file)
        total_score = cv_processor.extract_cv_details()
        try:
            #sending the total score for the token to the Ethereum contract
            tx_hash = self.contract_wrapper.receive_total_score_for_pair(int(token_id), total_score)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Total score received for token with ID of {token_id} : {total_score}")
        except Exception as e:
            print(f"Error processing token {token_id}: {e}")
        try:
            
            #updating the total score for the IPFS links on the Ethereum contract
            tx_hash = self.contract_wrapper.update_total_score(ipfs_link, second_part, total_score)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Total score received for the links {ipfs_link} and {second_part} : {total_score}")
            # Delete the decrypted files after processing
            self.delete_decrypted_files()
        except Exception as e:
            print(f"Error processing the links {ipfs_link} and {second_part}: {e}")

    #listening for events emitted by the Ethereum contract
    def listen_for_events(self):
        
        #filtering events emitted by the contract
        event_filter = self.contract_wrapper.get_event_filter()
        while True:
            try:
                #getting new event entries from the event filter
                logs = event_filter.get_new_entries()
                
                #iterating through each new event entry
                for log in logs:
                    
                    #evaluating the event
                    self.evaluate(log)
                    
            #Handle keyboard interrupt to exit the event listener
            except KeyboardInterrupt:
                print("Exiting event listener.")
                break
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    #defining contract address and private key (key taken from Ganache)
    contract_address = '0x8164C71ee2007299344216398b8f1F0E5387449b'
    private_key = '0x0e364996eb3e1314c3f11e981beb23d3ee6dc1a75885a35c3c479a69dc77bc04'
    
    #initializing the oracle instance
    oracle = Oracle(contract_address, private_key)
    
    #fetching all IPFS links and listening for events (for audit purpose)
    oracle.get_all_ipfs_links()
    #oracle.listen_for_events()
