Instruction to run the scripts:
-

Advert Retrieval
-
    advert_reading.py

Description:
This script allows you to download job adverts stored on the InterPlanetary File System (IPFS) and save them as HTML files.
Prerequisites:

- A running IPFS node or an accessible IPFS gateway. (IPFS Desktop App)
- Python 3 (The script uses pathlib)
- The ipfs_handler module. This custom module should be in the same directory or the parent directory of this script. The module should provide the following:

    -> Class IpfsHandle to handle IPFS interactions

    -> Exception class NoGatewayAvailable
  
How to Run:

1) Make sure you have an accessible IPFS gateway.
2) Place this script (advert_reader.py or your chosen filename) in a convenient directory.
3) Run the script from your terminal:

        python advert_reader.py 

Usage

- The script will prompt you to enter the Content ID of the job advert you want to download.
- Next, enter a filename (with an .html extension) for the downloaded advert.
- The file will be downloaded and saved with the provided filename.

Error Handling

- No Gateway Available: If the script cannot find an IPFS gateway, you'll see an error message. Ensure you have a node running or can access a gateway.
- Advert Data File Not Found: If the Content ID is incorrect, you'll get a message indicating the advert couldn't be found on IPFS.

Example Usage

    python advert_reader.py
    Enter the content ID: QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG  
    Enter a file name for the job advert (in HTML format):  software_engineer_advert.html
    File downloaded at: software_engineer_advert.html
---
Encrypting candidate CV
-
    CV_encryption.py
Description

This Python module provides functions to encrypt a CV (Curriculum Vitae) in XML format for secure transmission. It uses a combination of:

- Symmetric Encryption (AES): To encrypt the main CV content for efficiency.
- Asymmetric Encryption (RSA): To securely encrypt the AES key itself, ensuring only the intended recipient (who holds the private RSA key) can decrypt it.

Libraries

- cryptography: Provides the core cryptographic primitives and algorithms.

Encryption Process

1) Read CV: The read_cv_data function reads your CV file (must be in XML format).
2) Key Generation: The module generates a random 256-bit AES key (generate_aes_key) and an initialization vector (IV) (generate_iv) for AES encryption.
3) AES Encryption: The CV data is encrypted using AES in CBC mode with PKCS7 padding (encrypt_aes).
4) RSA Public Key: The module reads the employer's RSA public key from a file (read_rsa_public_key).
5) Split and Encrypt AES Key: The AES key is split into two halves, and each half is encrypted using RSA with OAEP padding (encrypt_with_rsa).
6) CV Packet Creation: A JSON 'CV packet' is created. This includes:
    - Header: Contains the IV (Base64 encoded) and the first half of the encrypted AES key (Base64 encoded).
    - Body: Contains the AES-encrypted CV data (Base64 encoded).

Output:

- The CV packet is written to a JSON file.
- The second half of the encrypted AES key is stored separately in another JSON file.

Usage

- Installation: Ensure you have the cryptography library installed 

        pip install cryptography

- RSA Keys: You need your own RSA private key and the employer's RSA public key (usually in PEM format).

- CV File: Your CV must be saved in XML format.

Example:

    python CV_encryption.py
    Enter the path to your CV file: CVs/CV_1.xml
    Enter the name of the file containing employer's public key: public_key.pem
    Enter the name of the folder where the CV packets should be stored: encrypted_CVs
    Enter the name for the CV packet JSON file: cv1_packet.json
    Enter the name for the symmetric key JSON file: cv1_second_part.json

