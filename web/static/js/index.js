var web3 = new Web3(window.ethereum);

var contract_address = "0xTODO";
var user_address = window.ethereum.selectedAddress;

// Initial function
async function init() {
    // it is assumed that the metamask is installed, so we dont need to check this
    await ethereum.enable();
}
init();

function is_not_valid(address) {
    return (address === "") || (!web3.utils.isAddress(address)) || (!address.startsWith('0x'));
}  

async function buy() {
}

async function withdraw() {
}