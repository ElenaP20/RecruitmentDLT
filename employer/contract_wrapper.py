from web3 import Web3
import json

class ContractWrapper:
    def __init__(self, contract_address, private_key):
        self.web3 = Web3(Web3.HTTPProvider('http://localhost:7546'))
        self.contract = self.web3.eth.contract(address=contract_address, abi=self.load_contract_abi())
        self.account_address = self.web3.eth.account.from_key(private_key).address

    def load_contract_abi(self):
        with open('abi.json', 'r') as f:
            return json.load(f)

    def get_all_ipfs_links(self, token_id):
        try:
            result = self.contract.functions.getAllIPFSLinks(token_id).call()
            token_ids = list(map(str, result[0]))
            ipfs_links = result[1]
            second_parts = result[2]
            data = {'tokens': []}
            for token_id, ipfs_link, second_part in zip(token_ids, ipfs_links, second_parts):
                if ipfs_link != "" and second_part != "":
                    data['tokens'].append({'tokenId': token_id, 'ipfsLink': ipfs_link, 'secondPart': second_part})
            return data
        except Exception as e:
            print("Error fetching IPFS links:", e)
            return None

    def read_json_data(self, file_path):
        try:
            with open(file_path, 'r') as json_file:
                return json.load(json_file)
        except Exception as e:
            print("Error reading JSON data:", e)
            return None

    def process_token(self, token_id, ipfs_link, second_part, total_score):
        try:
            tx_hash = self.contract.functions.receiveTotalScoreForPair(int(token_id), total_score).transact({
                'from': self.account_address,
            })
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Total score received for token with ID of {token_id} : {total_score}")
            tx_hash = self.contract.functions.updateTotalScore(ipfs_link, second_part, total_score).transact({
                'from': self.account_address,
            })
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Total score received for the links {ipfs_link} and {second_part} : {total_score}")
        except Exception as e:
            print(f"Error processing the links {ipfs_link} and {second_part}: {e}")

    def get_event_filter(self):
        return self.contract.events.TotalScoreCheck.create_filter(fromBlock='latest')
