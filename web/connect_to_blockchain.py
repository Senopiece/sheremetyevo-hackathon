import brownie.network.account
from brownie import project
from brownie import network
from brownie.network import accounts

from constants import CONTRACT_ADDRESS, OWNER_ADDRESS, DEBUG

owner_account, contract_container = [None] * 2


def connect():
    global owner_account, contract_container
    brownie_project = project.load('../streamed-payment', name='StreamedPayment')
    brownie_project.load_config()

    if DEBUG:
        network.connect('development')
    else:
        network.connect('production')

    if OWNER_ADDRESS is None:
        owner_account = network.accounts[0]
        # accounts[0].transfer(accounts[2], "1 ether")
        # accounts[0].transfer(accounts[3], "1 ether")
    else:
        owner_account = network.accounts.at(OWNER_ADDRESS, force=DEBUG)

    if CONTRACT_ADDRESS is None:
        brownie_project.IterableMapping.deploy({'from': owner_account})
        contract_container = brownie_project.Sheremetyevo.deploy({'from': owner_account})
    else:
        contract_container = brownie_project.Sheremetyevo.at(CONTRACT_ADDRESS)


def get_account(address) -> brownie.network.account.Account:
    return network.accounts.at(address, force=DEBUG)


if contract_container is None:
    connect()
    accounts[0].transfer("0x08AF794f6E06E873aa8Ef6B55F809Df6E3B7F493", "1 ether")
