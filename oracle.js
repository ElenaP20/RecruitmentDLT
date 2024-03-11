const { Web3 } = require('web3');
//to establish connection: address of Advert.sol, Ganache RPC, Advert.sol ABI json

//ABI
const contractABI = require('./abi.json');
//contract address
const contractAddress = '0x67685834122663C77fB09539ECC65CD33F11Eb1a';

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

        // Log or process the IPFS links and second parts
        console.log("IPFS Links:", ipfsLinks);
        console.log("Second Parts:", secondParts);
    } catch (error) {
        console.error("Error fetching IPFS links:", error);
    }
}

// Call the function to interact with the contract
getAllIPFSLinks();