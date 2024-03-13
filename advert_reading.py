import time
import json
from ipfs_handler import IpfsHandle, NoGatewayAvailable

def read_advert_data():
    ipfs_handler = IpfsHandle()
    # Wait for the JavaScript file to write the data
    time.sleep(1)  # Adjust the delay as needed
    
    try:
        # with open('advert_data.json', 'r') as f:
        #     advert_data = json.load(f)
        #     period_number = advert_data.get('periodNumber')
        #     content_id = advert_data.get('contentId')
        
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

# Call the function to read the advert data
content_id = read_advert_data()
