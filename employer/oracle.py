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
contract_address = '0xa8743e430b1F6e45e625B928CD6281FF074bB71e'
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
      
def getTokens():
    try:
        result = contract.functions.getTokens().call()
        print(result)
    except Exception as e:
        print("Error fetching IPFS tokens:", e)


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


# Run the main function
main()
# handle_event()
