let web3;
let contract;
let user_address;

// Initial function
async function init() {
    web3 = new Web3(window.ethereum);
    if (typeof window.ethereum === "undefined") {
        alert("Please install MetaMask") // AC-305-01
    } else {
        user_address = window.ethereum.selectedAddress;
        fetch("static/js/abi/Sheremetyevo.json")
            .then(response => response.json())
            .then(
                data => fetch("/contract-address").then(response => response.json()).then(address => {
                        contract = new web3.eth.Contract(data["abi"], address["address"]);
                    }
                ));
    }
}

function is_not_valid(address) {
    return (address === "") || (!web3.utils.isAddress(address)) || (!address.startsWith('0x'));
}

async function buy() {
    await init();
    contract.pay(user_address);
}

async function withdraw(amount) {
    await init();
    amount = parseFloat(amount);
    fetch("withdraw", {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        referrerPolicy: 'no-referrer',
        body: JSON.stringify({"amount": amount, "metamask_addr": user_address})
    }).then(response => alert(response.json()["status"]))
}