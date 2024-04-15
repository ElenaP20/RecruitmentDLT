# RecruitmentDLT
The code structure:

        RecruitmentDLT
        │
        ├── candidate
        │   ├── encryption
        │   │   ├── CVs
        │   │   │   ├── CV_1.xml
        │   │   │   ├── CV_2.xml
        │   │   │   ├── ...
        │   │   │   └── CV_10.xml
        │   │   ├── encrypted_CVs
        │   │   │   ├── cv1_packet.json
        │   │   │   ├── cv1_second_part.json
        │   │   │   ├── ...
        │   │   │   ├── cv10_packet.json
        │   │   │   └── cv10_second_part.json
        │   │   ├── CV_encryption.py
        │   │   └── public_key.pem
        │   ├── __init__.py
        │   └── advert_reading.py
        │
        ├── employer
        │   ├── advert
        │   │   ├── advert_1.html
        │   │   ├── advert_2.html
        │   │   ├── ...
        |   |   ├── advert_10.html
        │   |   └── key_generation.py
        │   ├── __init__.py
        │   ├── abi.json
        │   ├── combined_data.json
        │   ├── contract_wrapper.py
        │   ├── cv_parser.py
        │   ├── decryptor.py
        │   ├── file_processor.py
        │   ├── ipfs_data.json
        │   ├── key_value_extractor.py
        │   ├── oracle.py
        │   ├── private_key.pem
        |   └── public_key.pem
        ├── __init__.py
        └── ipfs_handler.py
In the displayed code structure, one script is used on both candidate and employer side (the _ipfs_handler.py_). This is because both sides fetch data from ipfs using content identifiers (CID).

Candidate side:
- The _advert_reading.py_ is used for the advert retrieval part of the process. The file prompts the user for input, which is the CID of a given advert and a name for the downloaded file. This script uses the ipfs handler to fetch the advert via the CID.
- The _CV_encryption.py_ is used after a CV has been prepared. The script encrypts a given CV( ending in xml) following the specified format and creates 2 JSON files.The first, labelled as packet, is submitted to the employer, whereas the second, i.e. second part, is submitted to the escrow. Users are asked for the path of their CV file (in xml), the path of the employer's public key (in PEM), the path of a folder where the output will be stored and the namings of the two JSON files. The public key should be downloaded from any of the adverts

Employer side:
- The key_generation.py is the script used for the generation of the public-private key pair, where the corresponding keys are stored in PEM files. The scipt creates the key pair using the RSA algorithms and stores the results as "private_key.pem" and "public_key.pem". The public key is added to all dummy adverts - advert_1.html to advert_10.html
**Note: The public_key.pem is found both on employer and candidate side, assuming the one on the candidate side is downloaded via the _advert_reading.py_ script**
- The _abi.json_ is the Application Binary Interface of the Advert.sol smart contract
- The _combined_data.json_ is an empty json file that is used whenever an auditor emits an event to check a score for a given submission pair. This file remains empty due to the data erasure functionality within the _oracle.py_.
- The _contract_wrapper.py_ is a complementary script that works together with the _oracle.py_ to establish a connection with the Ethereum smart contract (Advert.sol)
- The _cv_parser.py_ is used to extract the value from the decrypted CVs.
- The _decryptor.py_ decrypts the Cvs according to the specified format for the two JSON files.
- The _file_processor.py_ works togethere with the _key_value_extractor.py_ to extract key-value pairs from the downloaded JSON files (the two CV parts). The extracted dat is used in the _decryptor.py_
- The _ipfs_data.json_ is an empty json file, similar to the "_combined_data.json_", but it is used to store all submitted ipfs pairs for a given advert. After evaluating all apirs, the json file is emptied.
- The _oracle.py_ is the main script establishing a connection to the blockchain. To be successful it requires the contract address, where the Advert.sol is deployed on Remix IDE and the private key (taken from Ganache) of the Advert.sol contract owner (aka the employer). It triggers the following execution:
1. _contract_wrapper.py_, _abi.json_ and _file_processor.py_ upon initialization
2. _ipfs_handler.py_ to fetch the cv data files cv packet and cv second part)
3. _decryptor.py_ to decrypt the files
4. _cv_parser_ to extract the values given the shortlisting criteria and calculate the total score for a given pair
- The _private_key.pem_ is used in the _decryptor.py_ to decipher the plain text and the _public_key.pem_ is placed in the adverts
