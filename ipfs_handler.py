import json
import requests
from pathlib import Path
from typing import Union

#Exception for indicating no available gateways
class NoGatewayAvailable(Exception):
    pass

#class for handling IPFS data
class IpfsHandle:
    
    #list of public IPFS gateways
    PUBLIC_GATEWAYS = [
        "ipfs.io", "dweb.link", "w3s.link", "nft.storage.link", "cf-ipfs.com"
    ]

    def __init__(self):
        
        #flag to indicate whether to use local gateway
        self.use_local_gateway = True
        
        #the local gateway address (from IPFS App)
        self._local_gateway_address = "127.0.0.1:8080"
        
        #set to store downloaded files
        self._downloaded_files = set()

    #downloading file from URL
    def download(self, url, timeout=10) -> Path:
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                
                #generate unique file name and save the content
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

    #get file from IPFS network
    def get_file(self, content_id) -> Union[Path, str]:
        
        #determine gateway address
        gateway_address = self.get_valid_gateway()
        
        #get the download URL for a given content ID
        download_url = self.get_url(content_id, gateway_address)
        
        #download file and return file path and gateway address
        return self.download(download_url), gateway_address

    #generating unique file name
    def _generate_unique_file_name(self) -> str:
        index = 1
        while True:
            file_name = f"downloaded_file_{index}.json"
            if file_name not in self._downloaded_files:
                return file_name
            index += 1
    
    #test accessibility of a gateway
    def _test_gateway(self, gateway_address) -> bool:
        try:
            #test accessibility of gateway by sending a request
            response = requests.get(f"https://{gateway_address}")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    #test the accessibility of all public gateways
    @classmethod
    def _test_public_gateways(cls) -> list[bool]:
        results = []
        for address in cls.PUBLIC_GATEWAYS:
            result = cls._test_gateway(address)
            results.append(result)
        return results
    
    #get URL for accessing content on IPFS
    def get_url(self, content_id, gateway_address: str = None):
        if gateway_address is None or self.use_local_gateway:
            
            #use local gateway if no specific gateway provided or local gateway is preferred
            gateway_address = self._local_gateway_address
            return f"http://{self._local_gateway_address}/ipfs/{content_id}"
        #use specified gateway
        return f"https://{gateway_address}/ipfs/{content_id}"
  
    #get a valid gateway address  
    def get_valid_gateway(self) -> str:
        for gateway_address in self.PUBLIC_GATEWAYS:
             #iterate through public gateways to find a reachable one
            if self._test_gateway(gateway_address):
                return gateway_address
        #return local gateway if no public gateways are reachable
        return self._local_gateway_address
   
    #get the current gateway address 
    @property
    def gateway_address(self) -> str:
        if self.use_local_gateway:
            #return local gateway address if it's being used
            return self._local_gateway_address
        for gateway_address in self.PUBLIC_GATEWAYS:
            #iterate through public gateways to find a reachable one
            if self._test_gateway(gateway_address):
                return gateway_address
        #raise exception if no reachable gateway is found
        raise NoGatewayAvailable("All gateways are unreachable")

    #fetch token pairs from a JSON file
    def fetch_pairs_from_json(self, json_file):
        try:
            #open JSON file and extract token pairs
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
            #handle exceptions when fetching pairs from JSON
            print("Error fetching pairs from JSON:", e)
            return []