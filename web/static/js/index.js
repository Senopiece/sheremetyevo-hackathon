const abi = []

var web3 = new Web3(window.ethereum);

var contract_address = "0xTODO";
var user_address = window.ethereum.selectedAddress;

var contract = new web3.eth.Contract(abi, contract_address);

// Initial function
async function init() {
    // it is assumed that the metamask is installed, so we dont need to check this
    await ethereum.enable();
}
init();

async function buy() {
}

async function withdraw() {
}