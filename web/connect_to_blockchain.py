from brownie import project
from brownie import network

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
    else:
        owner_account = network.accounts.at(OWNER_ADDRESS, force=DEBUG)

    if CONTRACT_ADDRESS is None:
        brownie_project.IterableMapping.deploy({'from': owner_account})
        contract_container = brownie_project.Sheremetyevo.deploy({'from': owner_account})
    else:
        contract_container = brownie_project.Sheremetyevo.at(CONTRACT_ADDRESS)


if contract_container is None:
    connect()
