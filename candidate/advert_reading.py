import time
import sys
from pathlib import Path

# Add the parent directory of the current directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from employer.ipfs_handler import IpfsHandle, NoGatewayAvailable

class ReadAdvert:
    def read_advert_data(self):
        ipfs_handler = IpfsHandle()
        # Wait for the JavaScript file to write the data
        time.sleep(1)  # Adjust the delay as needed
        try:        
            # The following approach is for the user
            content_id = input("Enter the content ID: ")
            try:
                # Download the file with the given content ID
                file_path, _ = ipfs_handler.get_file(content_id)
                # Change the file extension to '.html' and specify the desired file name
                file_path_html = file_path.with_name('job_advert.html')
                file_path.rename(file_path_html)
                print(f"File downloaded at: {file_path_html}") 
                
            except NoGatewayAvailable as e:
                print("No gateway available:", e)
                # Return the content ID
            return content_id
        except FileNotFoundError:
            print("Advert data file not found.")
            return None, None

if __name__ == "__main__":
# Call the function to read the advert data
    readAd = ReadAdvert()
    content_id = readAd.read_advert_data()
