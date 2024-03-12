const { Web3 } = require('web3');
//to establish connection: address of Advert.sol, Ganache RPC, Advert.sol ABI json

//const axios = require('axios');

//ABI
const contractABI = require('./abi.json');
//contract address
const contractAddress = '0x5cADd1bCDeB8998562adb7f530755985308f7236';

//Ganache RPC runs on 127.0.0.1:7546
//const web3 = new Web3("http://localhost:7546")'

// Define the private key of the Ethereum account used for interaction
const privateKey = '0x410b11b0bb0a2de4d50b514de0268ebf97bf8f353fb66952296f9c066d028de7';

// Connect to the Ethereum network via a local Ganache RPC node
const web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:7546')); 

// Convert the private key into an Ethereum account object
const account = web3.eth.accounts.privateKeyToAccount(privateKey);

// Add the Ethereum account to the Web3 wallet
web3.eth.accounts.wallet.add(account);

// Set the default account to the Ethereum account
web3.eth.defaultAccount = account.address;

// Create an instance of the smart contract using its ABI and address
const contractInstance = new web3.eth.Contract(contractABI, contractAddress);


// Define an asynchronous function to interact with the contract
async function getAllIPFSLinks() {
    try {
        // Call the getAllIPFSLinks function of the smart contract to retrieve the IPFS links
        const result = await contractInstance.methods.getAllIPFSLinks().call();

        // Extracting IPFS links and second parts from the result
        const ipfsLinks = result[0];
        const secondParts = result[1];

//         // Iterate over each IPFS link
//         for (let i = 0; i < ipfsLinks.length; i++) {
//             const ipfsLink = ipfsLinks[i];
//             const secondPart = secondParts[i];

//             // Fetch encrypted data from IPFS link
//             const response = await axios.get(`http://127.0.0.1:8080/ipfs/${ipfsLink}`);
//             const encryptedData = response.data;

//             // Process the encrypted data as needed
//             console.log("Encrypted Data:", encryptedData);

//             // Process the second part of the data if needed
//             console.log("Second Part:", secondPart);
//         }
//     } catch (error) {
//         console.error("Error fetching IPFS links:", error);
//     }
// }
        // Log or process the IPFS links and second parts
        console.log("IPFS Links:", ipfsLinks.filter(link => link !== ''));
        console.log("Second Parts:", secondParts.filter(part => part !== ''));

    } catch (error) {
        console.error("Error fetching IPFS links:", error);
    }
}


// Call the function to interact with the contract
getAllIPFSLinks();

// const { Web3 } = require('web3');
// const fs = require('fs');
// const axios = require('axios');
// const CryptoJS = require('crypto-js');
// const forge = require('node-forge');

// // ABI
// const contractABI = require('./abi.json');
// // Contract address
// const contractAddress = '0xe8d73617137b3F9d768Aaee20F6a18Eb46411A94';
// // Private key
// const privateKey = '0x410b11b0bb0a2de4d50b514de0268ebf97bf8f353fb66952296f9c066d028de7';
// // Path to PEM file containing the secret key
// const pemFilePath = 'private_key.pem';

// // Connect to the Ethereum network via a local Ganache RPC node
// const web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:7546'));

// // Convert the private key into an Ethereum account object
// const account = web3.eth.accounts.privateKeyToAccount(privateKey);

// // Add the Ethereum account to the Web3 wallet
// web3.eth.accounts.wallet.add(account);

// // Set the default account to the Ethereum account
// web3.eth.defaultAccount = account.address;

// // Create an instance of the smart contract using its ABI and address
// const contractInstance = new web3.eth.Contract(contractABI, contractAddress);

// // Function to read the PEM file and extract the key
// function readPemFile(filePath) {
//     const pemData = fs.readFileSync(filePath, 'utf8');
//     const pemKey = forge.pki.privateKeyFromPem(pemData);
//     return forge.util.decode64(pemKey.n.toString(16));
// }

// // Define an asynchronous function to interact with the contract
// async function getAllIPFSLinks() {
//     try {
//         // Call the getAllIPFSLinks function of the smart contract to retrieve the IPFS links
//         const result = await contractInstance.methods.getAllIPFSLinks().call();

//         // Extracting IPFS links and second parts from the result
//         const ipfsLinks = result[0];
//         const secondParts = result[1];

//         // Log the IPFS links
//         console.log("IPFS Links:", ipfsLinks);

//         // Iterate over each IPFS link
//         for (let i = 0; i < ipfsLinks.length; i++) {
//             const ipfsLink = ipfsLinks[i];
//             const secondPart = secondParts[i];

//             // Fetch encrypted data from IPFS link
//             const response = await axios.get(ipfsLink);
//             const encryptedData = response.data;

//             // Extract half symmetric key from the header of the first part of the tuple
//             const halfSymmetricKeyEncrypted = JSON.parse(encryptedData).Header.HalfSymmetricKeyEncrypted;

//             // Read the secret key from the PEM file
//             const secretKey = readPemFile(pemFilePath);

//             // Decrypt the second part of the symmetric key
//             const decryptedSymmetricKeyPart2 = CryptoJS.AES.decrypt(halfSymmetricKeyEncrypted, secretKey).toString(CryptoJS.enc.Utf8);

//             // Combine the decrypted second part of the symmetric key with the half symmetric key
//             const fullSymmetricKey = halfSymmetricKey + decryptedSymmetricKeyPart2;

//             // Decrypt data using the full symmetric key
//             const decryptedData = CryptoJS.AES.decrypt(encryptedData, fullSymmetricKey, {
//                 mode: CryptoJS.mode.CBC,
//                 padding: CryptoJS.pad.Pkcs7
//             }).toString(CryptoJS.enc.Utf8);

//             // Log decrypted data
//             console.log("Decrypted Data:", decryptedData);
//         }
//     } catch (error) {
//         console.error("Error fetching IPFS links:", error);
//     }
// }

// // Call the function to interact with the contract
// getAllIPFSLinks();
