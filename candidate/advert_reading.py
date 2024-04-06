import time
import sys
from pathlib import Path

#adding the parent directory of the current directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from employer.ipfs_handler import IpfsHandle, NoGatewayAvailable

class ReadAdvert:
    def read_advert_data(self):
        ipfs_handler = IpfsHandle()
        try:        
            #user entering the content ID for a specific job advert
            content_id = input("Enter the content ID: ")
            try:
                #downloading the file with the given content ID
                file_path, _ = ipfs_handler.get_file(content_id)

                file_path_html = input("Enter a file name for the job advert (in HTML format): ")
                file_path.rename(file_path_html)
                print(f"File downloaded at: {file_path_html}") 
            
            #error handling for no gateway available
            except NoGatewayAvailable as e:
                print("No gateway available:", e)
            return content_id
        
        #error handling for no file found
        except FileNotFoundError:
            print("Advert data file not found.")
            return None, None

if __name__ == "__main__":
    #calling the function to read the advert data
    readAd = ReadAdvert()
    content_id = readAd.read_advert_data()
