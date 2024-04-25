# RecruitmentDLT
Folder structure:
--

                   employer
                   ├── advert
                   │   ├── advert_1.html
                   │   ├── advert_2.html
                   │   ├── ...
                   |   ├── advert_10.html
                   |   └── key_generation.py
                   ├── __init__.py
                   ├── abi.json
                   ├── combined_data.json
                   ├── contract_wrapper.py
                   ├── cv_parser.py
                   ├── decryptor.py
                   ├── file_processor.py
                   ├── ipfs_data.json
                   ├── key_value_extractor.py
                   ├── oracle.py
                   ├── private_key.pem
                   └── public_key.pem
                 

The script for handling IPFS content identifier(CID) is used on both candidate and employer side (the _ipfs_handler.py_), tehrefore located in the parent folder. 

Description of the scripts:
--
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

Running the employer side:
--
Only the _key_generation.py_ and _oracle.py_ scripts are run, since they trigger the execution of the remaining scripts.

1. For _key_generation.py_, you will have to navigate to the subfolder:
   
        cd advert
   
   Then run in the terminal or command prompt:
   
        python key_generation.py

2. For _oracle.py_, simply run:
   
        python oracle.py
   Example inputs:
   
        Enter the address where Advert.sol is deployed: _0xF853259a187910d635b073A4b367dBEf956F027a_
   
        Enter the private key of the owner: _0xeaddecf2972e1d3a5a91120d1844fa0d5d80edd935863e93805866823f843b0f_
   
        Enter the advert ID: _111_
