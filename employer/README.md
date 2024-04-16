Instruction on how to use the following scripts:
-
The RSA key generation script
-
    key_generation.py

Description

- This Python script generates a new RSA key pair (private and public key) and saves them in the standard PEM format. 

Libraries

- cryptography: The core library providing the cryptographic functions for:
    - serialization: Converting cryptographic keys into formats suitable for storage and transmission (like PEM).
    - asymmetric (RSA): Generating and handling RSA key pairs.

Process

- RSA Key Generation:

    - Creates a 2048-bit RSA private key. The public key is mathematically derived from the private key.
- PEM Serialization:

    - Private Key: The private key is serialized in the traditional PEM format without any password protection (serialization.NoEncryption())
    - Public Key: The public key is serialized into PEM format, specifically the SubjectPublicKeyInfo format commonly used to share public keys.

File Storage:

- private_key.pem: The serialized private key should be kept secure
- public_key.pem: The serialized public key is shared with others who need to encrypt data that only the private key can decrypt.

Note:

- PEM is a standard way of encoding cryptographic keys, making them easy to store and transmit.

How to Use

Make sure you have the cryptography library installed 

    pip install cryptography

Run the script. It will generate the two PEM files.

    python key_generation.py
    Enter a filename for your private key (include .pem): my_private_key.pem
    Enter a filename for your public key (include .pem): my_public_key.pem
    Private key stored in my_private_key.pem
    Public key stored in my_public_key.pem

Important Notes on Key Usage

- Default Key Pair: The job advert creation system relies on pre-generated public and private keys named "public_key.pem" and "private_key.pem".  Any CVs encrypted with this system must use the same public key.

Generating New Keys:  If you want to use a different key pair:

1) Generate Keys: Use the key_generation.py script to create a new public and private key pair.
2) Encryption: When encrypting a CV, provide the path to your newly generated public key.
3) Decryption: Ensure you use the corresponding newly generated private key to decrypt the CV.

Key Points

- The encryption and decryption processes must use matching public and private key pairs for successful communication.
---
Connecting the local oracle to Ethereum
-
    oracle.py

Description

- This Python project implements a decentralized system for evaluating encrypted job applications stored on IPFS (InterPlanetary File System). 
- It leverages Ethereum smart contracts to manage the evaluation process and securely record scores.

Key Features

- Secure Storage: Job applications (CVs) are encrypted and stored on IPFS, ensuring confidentiality.
- Evaluation: Evaluation logic is implemented independently from the Ethereum smart contract, allowing for flexible scoring mechanisms.
- Auditing: The system includes functionality to audit past evaluations based on events emitted by the smart contract.
- Flexibility: The CV processing and scoring logic (CVProcessor) can be customized to accommodate different evaluation criteria.

Components

- Oracle Class: Interacts with the Ethereum contract, handles IPFS links, decrypts CVs, and manages evaluation.
- ContractWrapper Class: Simplifies interactions with the Ethereum smart contract.
- Decryption Class: Handles secure decryption of CV data.
- FileProcessor Class: Provides basic file-related operations.
- CVProcessor Class: Extracts relevant data from CVs and implements scoring logic.
- IpfsHandle Class: Manages file uploads/downloads from IPFS.

Dependencies

- Web3.py: For interacting with the Ethereum blockchain.
- cryptography: For cryptographic operations (encryption/decryption).
- IPFS Node: necessary for the IpfsHandler class
- Ganache: A local Ethereum development blockchain 

Setup

A connection between Remix IDE, Ganache and the local oracle (oracle.py) must be established:
1) Deploy the Advert.sol smart contract to Remix IDE, by connecting it to Ganache: 
    
    Ganache is a valuable tool for testing smart contracts in a local Ethereum environment. Let's break down how to set it up and connect it with Remix IDE:

    1. Download and Install

    Get the Ganache app from the official website (https://trufflesuite.com/ganache/). Follow the instructions for your operating system.

    2. Create a Workspace

    Launch Ganache and click "NEW WORKSPACE".

        Important: 
        In the workspace settings, make sure the "HARDFORK" matches the Remix IDE's EVM environment. For the development of this process, the environment is "London"

    3. Accounts and Test ETH

    Ganache workspace provides several test accounts. Each comes pre-loaded with 100 test ETH for development and testing purposes.

        Keys:
        For the oracle script, you'll need the private key of the account you want the oracle to use. This private key is passed to the oracle.py. In the main block, just copy and paste the private key.

        Important:
        Once Remix IDE is connected to Ganache, by default the first account will be selected in the "Deploy and run transactions tab". If you deploy the three smart contracts with that default selection, the first account displayed in the Ganache workspace is the owner (aka employer). Therefore, the private key that is used in the oracle.py should be the one of the owner, which is the first account. 
        
        Switching Accounts: 
        In Remix, use the "Account" dropdown (in "Deploy & Run Transactions") to switch between test accounts if needed.
        
        Need More ETH: 
        Simply create a new workspace if you deplete your test ETH.
    4. Connect to Remix IDE

    In Remix, select the "Deploy & Run Transactions" tab.
    In the "Environment" dropdown, choose "Dev - Ganache Provider".
    5. Configuration: 
    
    In the main block:

    Update the contract_address with the deployed smart contract address. 

        contract_address = '0x79E5e3A5E9F35724dc2eBa917A2312C6b8050691'

    Update the private key to the one corresponding to the owner. If owner is by default the first one from the list of accounts in Ganache, use the corresponding private key. (taken from Ganache)

        private_key = '0xa5b94567be428698d8b6e622feed9c79e1770d6100179b707d810bbd8d87abf8'

    In the Oracle and ContractWrapper initializer:

    Update the localhost in both the oracle.py and contract_wrapper.py with the RPC SERVER in the Ganache workspace  

        self.web3 = Web3(Web3.HTTPProvider('http://localhost:7542'))


IPFS:
- Ensure you have an accessible IPFS node or gateway. This is done by downloading IPFS Desktop App(https://docs.ipfs.tech/install/ipfs-desktop/) . The application must be running throughout the oracle evaluation process.

Usage

- Encrypt CVs: Encrypt CVs using the provided encryption module and the employer's public key.
- Upload to IPFS: Upload encrypted CVs to IPFS and obtain their IPFS links.
- Run the Script: Execute the Python script (oracle.py), which will:
    - Fetch IPFS links from the smart contract.
    - Download, decrypt, and process CVs.
    - Calculate scores.
    - Submit scores back to the smart contract.
    
Auditing

The script listens for events emitted by the smart contract. If an audit is triggered:

- It retrieves the relevant IPFS links and scores from the event.
- Downloads and decrypts the associated CVs.
- Recalculates the score.
- Submits the recalculated score to the contract.
