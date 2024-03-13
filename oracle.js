const { Web3 } = require('web3');
const fs = require('fs'); // Import Node.js file system module
//to establish connection: address of Advert.sol, Ganache RPC, Advert.sol ABI json

//const axios = require('axios');

//ABI
const contractABI = require('./abi.json');
//contract address
const contractAddress = '0x5cF0B926373eC84Aca43Ffe695B69461efE613a4';

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
        const result = await contractInstance.methods.getAllIPFSLinks().call();

        const ipfsLinks = result[0];
        const secondParts = result[1];

        // Construct an object containing IPFS links and second parts
        const data = {
            ipfsLinks: ipfsLinks.filter(link => link !== ''),
            secondParts: secondParts.filter(part => part !== '')
        };

        // Convert the data object to JSON
        const jsonData = JSON.stringify(data, null, 2);

        // Write the JSON data to a file
        fs.writeFileSync('ipfs_data.json', jsonData, 'utf-8');

        console.log("Data written to ipfs_data.json successfully.");

    } catch (error) {
        console.error("Error fetching IPFS links:", error);
    }
}
// Define an asynchronous function to interact with the contract and write the result to a file
async function getAdvertData() {
    try {
        const result = await contractInstance.methods.getAdvert().call();
        // convert from BigInt to int
        //const periodNumber = Number(result[0]);
        const contentId = result[1];
        
        console.log("The content ID is: ", contentId)
        // // Write the result to a JSON file
        // const data = { periodNumber, contentId };
        // require('fs').writeFileSync('advert_data.json', JSON.stringify(data));
    } catch (error) {
        console.error("Error fetching the advert:", error);
    }
}
//to retrieve the advert - returns the content ID (used later in the advert_reading.py)
getAdvertData() 
//to retrieve the submitted cvs
getAllIPFSLinks()
