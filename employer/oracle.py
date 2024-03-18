from web3 import Web3
import json
from ipfs_handler import IpfsHandle
from decryptor import Decryption
from file_processor import FileProcessor
from cv_parser import CVProcessor
from pathlib import Path

# Initialize web3 instance
web3 = Web3(Web3.HTTPProvider('http://localhost:7546'))

# Contract address and ABI
contract_address = '0xC573299d9c4Dfee429Be2223562C02D758b0438e'
with open('abi.json', 'r') as f:
    contract_abi = json.load(f)

# Account details
private_key = '0x410b11b0bb0a2de4d50b514de0268ebf97bf8f353fb66952296f9c066d028de7'
account_address = web3.eth.account.from_key(private_key).address

# Contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def get_all_ipfs_links():
    token_id = 111
    try:
        result = contract.functions.getAllIPFSLinks(token_id).call()
        token_ids = list(map(str, result[0]))
        ipfs_links = result[1]
        second_parts = result[2]

        data = {'tokens': []}

        for token_id, ipfs_link, second_part in zip(token_ids, ipfs_links, second_parts):
            if ipfs_link != "" and second_part != "":
                data['tokens'].append({
                    'tokenId': token_id,
                    'ipfsLink': ipfs_link,
                    'secondPart': second_part,
                })

        # Write data to JSON file
        with open('ipfs_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=2)
        
        print("Data written to ipfs_data.json successfully.")
        
    except Exception as e:
        print("Error fetching IPFS links:", e)
      
# def getTokens():
#     try:
#         result = contract.functions.getTokens().call()
#         print(result)
#     except Exception as e:
#         print("Error fetching IPFS tokens:", e)

def main():
    # Run the function to fetch tokens and IPFS links
    get_all_ipfs_links()

    # Read JSON data from file
    with open('ipfs_data.json', 'r') as json_file:
        data = json.load(json_file)
        tokens = data.get('tokens', [])

        # Loop through each token
        for index, token in enumerate(tokens, start=1):
            token_id = token.get('tokenId')
            ipfs_link = token.get('ipfsLink')
            second_part = token.get('secondPart')

            # Initialize IpfsHandle instance
            handler = IpfsHandle()

            # Download the first file
            downloaded_file_path1, _ = handler.get_file(ipfs_link)
            print(f"File downloaded at: {downloaded_file_path1}")

            # Download the second file
            downloaded_file_path2, _ = handler.get_file(second_part)
            print(f"File downloaded at: {downloaded_file_path2}")

            # Initialize FileProcessor instances for each pair
            file_processor1 = FileProcessor()

            # Initialize Decryption instances for each pair
            decryption1 = Decryption(downloaded_file_path1, downloaded_file_path2, "private_key.pem", file_processor1)

            # Process decryption for the pair of files
            decryption1.process()

            # Call CVProcessor to extract CV details from decrypted XML files
            xml_files = [f"decrypted_file_{index}.xml"]
            cv_processor = CVProcessor(xml_files, 'ipfs_data.json')
            total_score = cv_processor.extract_cv_details()

            # Call the smart contract function to receive the total score for the pair
            try:
                tx_hash = contract.functions.receiveTotalScoreForPair(int(token_id), total_score).transact({
                    'from': account_address,
                })
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"Total score received for token with ID of {token_id} : {total_score}")
            except Exception as e:
                print(f"Error processing token {token_id}: {e}")
            try:
                tx_hash = contract.functions.updateTotalScore(ipfs_link, second_part, total_score).transact({
                    'from': account_address,
                })
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"Total score received for the links {ipfs_link} and {second_part} : {total_score}")
            except Exception as e:
                print(f"Error processing the links {ipfs_link} and {second_part}: {e}")


def evaluate(token_id, ipfs_link, second_part,score, ipfs_file):
    # Initialize IpfsHandle instance
            handler = IpfsHandle()

            # Download the first file
            downloaded_file_path1, _ = handler.get_file(ipfs_link)
            print(f"File downloaded at: {downloaded_file_path1}")

            # Download the second file
            downloaded_file_path2, _ = handler.get_file(second_part)
            print(f"File downloaded at: {downloaded_file_path2}")

            # Initialize FileProcessor instances for each pair
            file_processor1 = FileProcessor()

            # Initialize Decryption instances for each pair
            decryption1 = Decryption(downloaded_file_path1, downloaded_file_path2, "private_key.pem", file_processor1)

            # Process decryption for the pair of files
            #xml_file = decryption1.process()

            # Call CVProcessor to extract CV details from decrypted XML files
            xml_file = [f"decrypted_file_1.xml"]
            cv_processor = CVProcessor(xml_file, ipfs_file)
            total_score = cv_processor.extract_cv_details()

            # Call the smart contract function to receive the total score for the pair
            try:
                tx_hash = contract.functions.receiveTotalScoreForPair(int(token_id), total_score).transact({
                    'from': account_address,
                })
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"Total score received for token with ID of {token_id} : {total_score}")
            except Exception as e:
                print(f"Error processing token {token_id}: {e}")
            try:
                tx_hash = contract.functions.updateTotalScore(ipfs_link, second_part, total_score).transact({
                    'from': account_address,
                })
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"Total score received for the links {ipfs_link} and {second_part} : {total_score}")
            except Exception as e:
                print(f"Error processing the links {ipfs_link} and {second_part}: {e}")
# Run the main function
#main()
# handle_event()
# Function to handle TotalScoreReceived event
def handle_event(event):
    print("Total Score Received event detected!")
    _tokenId = event['args']['_tokenId']
    link1 = event['args']['ipfsLink1']
    link2 = event['args']['ipfsLink2']
    score = event['args']['totalScore']
    print("TokenId:", _tokenId)
    print("IPFS Link 1:", link1)
    print("IPFS Link 2:", link2)
    print("Total Score:", score)
    print("Evaluation started...")
    # Combine the processed content into a dictionary
    combined_data = {
        "ipfsLink1": link1,
        "ipfsLink2": link2
    }

    # Write the combined data to a JSON file
    with open('combined_data.json', 'w') as json_file:
        json.dump(combined_data, json_file)

    # Pass the created JSON file along with other parameters to the evaluate function
    evaluate(_tokenId, link1, link2, score, 'combined_data.json')

    
# Create event filter for TotalScoreCheck event
event_filter = contract.events.TotalScoreCheck.create_filter(fromBlock='latest')

# Main loop to listen for events
while True:
    try:
        # Get new event logs
        logs = event_filter.get_new_entries()
        for log in logs:
            handle_event(log)
    except KeyboardInterrupt:
        print("Exiting event listener.")
        break
    except Exception as e:
        print("Error:", e)