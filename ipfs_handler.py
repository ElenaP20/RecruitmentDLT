from pathlib import Path
from typing import Optional
import requests
import json
from typing import Union

class NoGatewayAvailable(Exception):
    pass


class IpfsHandle:
    
    #List of public gateways - not often online
    #reference list for gateways - https://ipfs.github.io/public-gateway-checker/
    PUBLIC_GATEWAYS = [
        "ipfs.io", "dweb.link", "w3s.link", "nft.storage.link", "cf-ipfs.com"
    ]
    #"trustless-gateway.link", "cf-ipfs.com", "ipfs.eth.aragon.network", "cloudflare-ipfs.com", "hardbin.com"
    def __init__(self):
        self.use_local_gateway = True #set true to prioritize the local gateway
        self._local_gateway_address = "127.0.0.1:8080" #default local gateway IPFS Desktop app
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
        #get a valid gateway address and download the content
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
    
    @staticmethod
    def _test_gateway(gateway_address) -> bool:
        #Test the availability of a specific gateway by sending a request
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
    
    def get_url(self, content_id, gateway_address: Optional[str] = None):
        if gateway_address is None or self.use_local_gateway:
            gateway_address = self._local_gateway_address
            return f"http://{self._local_gateway_address}/ipfs/{content_id}"
        # Construct the URL to access the content based on CID and gateway address
        # This does not work with IPNS
        return f"https://{gateway_address}/ipfs/{content_id}"
    
    def get_valid_gateway(self) -> str:
        # Find a valid public gateway or use the local node as a fallback
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
        
if __name__ == "__main__":
    ipfs_handler = IpfsHandle()
    
    # Faster way is:
    # content_ids = [
    #     "QmZqRiJvuDNZJXAZxyzeeQzsdwQMGT53G7YsK7LnAnrgVw",
    #     "QmNcjqHNZtYtyu93ExwtHGmxDn19zZUj8VVJGvcn7NHgGq",
    #     # Add more content IDs as needed
    # ]
    
    # Define the content IDs
    part_one = "QmZqRiJvuDNZJXAZxyzeeQzsdwQMGT53G7YsK7LnAnrgVw"
    part_two = "QmNcjqHNZtYtyu93ExwtHGmxDn19zZUj8VVJGvcn7NHgGq"
    
    downloaded_file_path1, gateway_address1 = ipfs_handler.get_file(part_one)
    downloaded_file_path2, gateway_address2 = ipfs_handler.get_file(part_two)
    
    print(f"File downloaded at: {downloaded_file_path1}") 
    print(f"File downloaded at: {downloaded_file_path2}") 
    
    # Create a dictionary to store the details
    ipfs_details = {
        "part_one": {
            "file_path": str(downloaded_file_path1),
            "content_id": part_one
        },
        "part_two": {
            "file_path": str(downloaded_file_path2),
            "content_id": part_two
        }
    }
    
    # Save the details to a JSON file
    with open("ipfs_details.json", "w") as json_file:
        json.dump(ipfs_details, json_file)
    