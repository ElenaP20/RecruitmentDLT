const { Web3 } = require('web3');
const fs = require('fs');
const {exec} = require('child_process');

const contractABI = require('./abi.json');
const contractAddress = '0xBF841067964A80fA5e9C38dE44fC5cAD20dcDf71';
const privateKey = '0x410b11b0bb0a2de4d50b514de0268ebf97bf8f353fb66952296f9c066d028de7';
const web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:7546'));
const account = web3.eth.accounts.privateKeyToAccount(privateKey);
web3.eth.accounts.wallet.add(account);
web3.eth.defaultAccount = account.address;
const contractInstance = new web3.eth.Contract(contractABI, contractAddress);

async function getAllIPFSLinks() {
    try {
        const result = await contractInstance.methods.getAllIPFSLinks().call();
        const tokenIds = result[0].map(id => id.toString()); // Convert BigInt to string
        const ipfsLinks = result[1];
        const secondParts = result[2];

        const data = {
            tokens: []
        };

        for (let i = 0; i < tokenIds.length; i++) {
            const tokenId = tokenIds[i];
            const ipfsLink = ipfsLinks[i];
            const secondPart = secondParts[i];
            // Check if both ipfsLink and secondPart are not empty strings
            if (ipfsLink !== "" && secondPart !== "") {
                // Push token data to the data object
                data.tokens.push({
                    tokenId: tokenId,
                    ipfsLink: ipfsLink,
                    secondPart: secondPart
                });
            }
        }

        // Convert data object to JSON string
        const jsonData = JSON.stringify(data, null, 2);

        // Write JSON string to file
        fs.writeFileSync('ipfs_data.json', jsonData, 'utf-8');
        
        console.log("Data written to ipfs_data.json successfully.");

    } catch (error) {
        console.error("Error fetching IPFS links:", error);
    }
}

getAllIPFSLinks();