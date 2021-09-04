const abi = []

var web3 = new Web3(window.ethereum);
if (typeof window.ethereum === "undefined") {
    alert("Please install MetaMask") // AC-305-01
} else {
// Initial function
    async function init() {
        if (typeof window.ethereum === "undefined") {
            alert("Please install MetaMask") // AC-305-01
        } else {
            // var abi;
            var contract_address = "0xTODO";
            var user_address = window.ethereum.selectedAddress;
            fetch("static/js/abi/Sheremetyevo.json")
                .then(response => {
                    return response.json();
                })
                .then(
                    abi => {
                        var contract = new web3.eth.Contract(abi, contract_address);
                        console.log(contract);
                    }
                );
            // var contract = new web3.eth.Contract(abi, contract_address);
            // console.log(user_address, contract, contract_address);
        }
    }

    init();

    function is_not_valid(address) {
        return (address === "") || (!web3.utils.isAddress(address)) || (!address.startsWith('0x'));
    }

    async function buy() {
    }

    async function withdraw() {
    }
}