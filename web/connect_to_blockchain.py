from brownie import project
from brownie import network

from constants import CONTRACT_ADDRESS, OWNER_ADDRESS, DEBUG

brownie_project = project.load('../streamed-payment', name='StreamedPayment')
brownie_project.load_config()

from brownie.project.StreamedPayment import *

if DEBUG:
    network.connect('development')
else:
    network.connect('production')

if OWNER_ADDRESS is None:
    owner_account = network.accounts[0]
else:
    owner_account = network.accounts.at(OWNER_ADDRESS)

if CONTRACT_ADDRESS is None:
    IterableMapping.deploy({'from': owner_account})
    contract_container = Sheremetyevo.deploy({'from': owner_account})
    print('Contract deployed at', contract_container.address)
else:
    contract_container = Sheremetyevo.at(CONTRACT_ADDRESS)
