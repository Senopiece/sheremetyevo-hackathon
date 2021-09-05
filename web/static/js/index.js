let web3;
let contract;
let user_address;
let contract_address;

// Initial function
async function init() {
    web3 = new Web3(window.ethereum);
    if (typeof window.ethereum === "undefined") {
        alert("Please install MetaMask") // AC-305-01
    } else {
        user_address = window.ethereum.selectedAddress;
        let data = fetch("static/js/abi/Sheremetyevo.json").then(response => response.json());
        contract_address = (await fetch("/contract-address").then(response => response.json()))["address"];
        data = await data;
        contract = new web3.eth.Contract(data["abi"], contract_address);
    }
}

function is_not_valid(address) {
    return (address === "") || (!web3.utils.isAddress(address)) || (!address.startsWith('0x'));
}

async function buy(amount) {
    await init();
    let terminal_address = (await fetch("/user-address").then(response => response.json()))["address"];
    let tx = await contract.methods.pay(terminal_address).send(
        {
            from: user_address,
            value: parseFloat(amount),
            nonce: 1
        }
    );
    await fetch("/buy", {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        referrerPolicy: 'no-referrer',
        body: JSON.stringify({"tx_hash": tx.transactionHash})
    });
    Location.reload()
}

async function withdraw(amount) {
    await init();
    amount = parseFloat(amount);
    fetch("/withdraw", {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        referrerPolicy: 'no-referrer',
        body: JSON.stringify({"amount": amount, "metamask_addr": user_address})
    }).then(response => response.json().then(
        json => {
            alert(json["status"]);
            Location.reload()
        })
    )
}