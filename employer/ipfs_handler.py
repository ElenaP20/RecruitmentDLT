import json
import requests
from pathlib import Path
from typing import Union
#from decryptor import Decryption
#from file_processor import FileProcessor
#from cv_parser import CVProcessor
#from CV_decryption import Decryption, FileProcessor

class NoGatewayAvailable(Exception):
    pass

class IpfsHandle:
    PUBLIC_GATEWAYS = [
        "ipfs.io", "dweb.link", "w3s.link", "nft.storage.link", "cf-ipfs.com"
    ]

    def __init__(self):
        self.use_local_gateway = True
        self._local_gateway_address = "127.0.0.1:8080"
        self._downloaded_files = set()

    def download(self, url, timeout=10) -> Path:
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                file_name = self._generate_unique_file_name()
                file_path = Path(file_name)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                self._downloaded_files.add(file_name)
                return file_path
            else:
                raise Exception(f"Failed to download file from {url}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_file(self, content_id) -> Union[Path, str]:
        gateway_address = self.get_valid_gateway()
        download_url = self.get_url(content_id, gateway_address)
        return self.download(download_url), gateway_address

    def _generate_unique_file_name(self) -> str:
        index = 1
        while True:
            file_name = f"downloaded_file_{index}.json"
            if file_name not in self._downloaded_files:
                return file_name
            index += 1
    
    def _test_gateway(self, gateway_address) -> bool:
        try:
            response = requests.get(f"https://{gateway_address}")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    @classmethod
    def _test_public_gateways(cls) -> list[bool]:
        results = []
        for address in cls.PUBLIC_GATEWAYS:
            result = cls._test_gateway(address)
            results.append(result)
        return results
    
    def get_url(self, content_id, gateway_address: str = None):
        if gateway_address is None or self.use_local_gateway:
            gateway_address = self._local_gateway_address
            return f"http://{self._local_gateway_address}/ipfs/{content_id}"
        return f"https://{gateway_address}/ipfs/{content_id}"
    
    def get_valid_gateway(self) -> str:
        for gateway_address in self.PUBLIC_GATEWAYS:
            if self._test_gateway(gateway_address):
                return gateway_address
        return self._local_gateway_address
    
    @property
    def gateway_address(self) -> str:
        if self.use_local_gateway:
            return self._local_gateway_address
        for gateway_address in self.PUBLIC_GATEWAYS:
            if self._test_gateway(gateway_address):
                return gateway_address
        raise NoGatewayAvailable("All gateways are unreachable")

    def fetch_pairs_from_json(self, json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                token_pairs = []
                for token in data.get('tokens', []):
                    ipfs_link = token.get('ipfsLink')
                    second_part = token.get('secondPart')
                    if ipfs_link and second_part:
                        token_pairs.append((ipfs_link, second_part))
                return token_pairs
        except Exception as e:
            print("Error fetching pairs from JSON:", e)
            return []

# if __name__ == "__main__":
#     ipfs_handler = IpfsHandle()
#     json_file_path = "ipfs_data.json"
#     token_pairs = ipfs_handler.fetch_pairs_from_json(json_file_path)
    
#     for index, (part_one, part_two) in enumerate(token_pairs, start=1):
#         downloaded_file_path1, gateway_address1 = ipfs_handler.get_file(part_one)
#         downloaded_file_path2, gateway_address2 = ipfs_handler.get_file(part_two)
        
#         print(f"Pair {index}:")
#         print(f"File downloaded at: {downloaded_file_path1}") 
#         print(f"File downloaded at: {downloaded_file_path2}")
        
#         # Initialize FileProcessor instances for each pair
#         file_processor1 = FileProcessor()
        
#         # Initialize Decryption instances for each pair
#         decryption1 = Decryption(downloaded_file_path1, downloaded_file_path2, "private_key.pem", file_processor1)

#         # Process decryption for the first pair of files
#         decryption1.process()
        
#         # Call CVProcessor to extract CV details from decrypted XML files
#         xml_files = [f"decrypted_file_{index}.xml"]
#         cv_processor = CVProcessor(xml_files, json_file_path)
#         cv_processor.extract_cv_details()

    
        

