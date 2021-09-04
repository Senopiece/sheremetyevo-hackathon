import os
from pprint import pprint
import xrpl
from dotenv import load_dotenv

load_dotenv()

RPC_CLIENT_URL = os.getenv('RPC_CLIENT_URL')
ACCOUNT_ADDRESS = os.getenv('ACCOUNT_ADDRESS')


if __name__ == '__main__':
    print('Hello from oracle!')
    client = xrpl.clients.JsonRpcClient(RPC_CLIENT_URL)
    print('Transactions for test account:')
    pprint(xrpl.account.get_account_transactions(ACCOUNT_ADDRESS, client))
