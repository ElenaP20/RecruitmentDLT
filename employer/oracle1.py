from web3 import Web3
import json
from ipfs_handler import IpfsHandle
from decryptor import Decryption
from file_processor import FileProcessor
from cv_parser import CVProcessor
from pathlib import Path
from contract_wrapper import ContractWrapper

class Oracle:
    def __init__(self, contract_address, private_key):
        self.web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))
        self.contract_wrapper = ContractWrapper(contract_address, private_key)
        self.file_processor = FileProcessor()  

    def get_all_ipfs_links(self):
        try:
            result = self.contract_wrapper.get_all_ipfs_links(111)
            if result:
                with open('ipfs_data.json', 'w') as json_file:
                    json.dump(result, json_file, indent=2)
                print("Data written to ipfs_data.json successfully.")
                print("Evaluation has started...")
                self.process_tokens()
        except Exception as e:
            print("Error fetching IPFS links:", e)

    def process_tokens(self):
        data = self.contract_wrapper.read_json_data('ipfs_data.json')
        if data:
            for index, token in enumerate(data.get('tokens', []), start=1):
                token_id = token.get('tokenId')
                ipfs_link = token.get('ipfsLink')
                second_part = token.get('secondPart')
                handler = IpfsHandle()
                downloaded_file_path1, _ = handler.get_file(ipfs_link)
                downloaded_file_path2, _ = handler.get_file(second_part)
                decryption = Decryption(downloaded_file_path1, downloaded_file_path2, "private_key.pem", self.file_processor)  
                decryption.process()
                xml_files = [f"decrypted_file_{index}.xml"]
                cv_processor = CVProcessor(xml_files, 'ipfs_data.json')
                total_score = cv_processor.extract_cv_details()
                self.contract_wrapper.process_token(token_id, ipfs_link, second_part, total_score)

    def evaluate(self, event):
        _tokenId = event['args']['_tokenId']
        link1 = event['args']['ipfsLink1']
        link2 = event['args']['ipfsLink2']
        score = event['args']['totalScore']
        print("TokenId:", _tokenId)
        print("IPFS Link 1:", link1)
        print("IPFS Link 2:", link2)
        print("Total Score:", score)
        print("Evaluation started...")
        combined_data = {"ipfsLink1": link1, "ipfsLink2": link2}
        with open('combined_data.json', 'w') as json_file:
            json.dump(combined_data, json_file)
        self.process_evaluation(_tokenId, link1, link2, score, 'combined_data.json')

    def process_evaluation(self, token_id, ipfs_link, second_part, score, ipfs_file):
        handler = IpfsHandle()
        downloaded_file_path1, _ = handler.get_file(ipfs_link)
        downloaded_file_path2, _ = handler.get_file(second_part)
        decryption = Decryption(downloaded_file_path1, downloaded_file_path2, "private_key.pem")
        decryption.process()
        xml_files = [f"decrypted_file_1.xml"]
        cv_processor = CVProcessor(xml_files, ipfs_file)
        total_score = cv_processor.extract_cv_details()
        try:
            tx_hash = self.contract_wrapper.receive_total_score_for_pair(int(token_id), total_score)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Total score received for token with ID of {token_id} : {total_score}")
        except Exception as e:
            print(f"Error processing token {token_id}: {e}")
        try:
            tx_hash = self.contract_wrapper.update_total_score(ipfs_link, second_part, total_score)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Total score received for the links {ipfs_link} and {second_part} : {total_score}")
        except Exception as e:
            print(f"Error processing the links {ipfs_link} and {second_part}: {e}")

    def listen_for_events(self):
        event_filter = self.contract_wrapper.get_event_filter()
        while True:
            try:
                logs = event_filter.get_new_entries()
                for log in logs:
                    self.evaluate(log)
            except KeyboardInterrupt:
                print("Exiting event listener.")
                break
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    contract_address = '0xC573299d9c4Dfee429Be2223562C02D758b0438e'
    private_key = '0x410b11b0bb0a2de4d50b514de0268ebf97bf8f353fb66952296f9c066d028de7'
    oracle = Oracle(contract_address, private_key)
    oracle.get_all_ipfs_links()
    oracle.listen_for_events()
