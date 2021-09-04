import os
import asyncio
from pprint import pprint
from typing import List
from itertools import groupby
import xrpl.asyncio
from dotenv import load_dotenv
from oracle.data_models import Transaction

load_dotenv()

RPC_CLIENT_URL = os.getenv('RPC_CLIENT_URL')
ACCOUNT_ADDRESS = os.getenv('ACCOUNT_ADDRESS')
CLIENT = xrpl.asyncio.clients.AsyncJsonRpcClient(RPC_CLIENT_URL)


async def get_incoming_payments() -> dict[str, List[Transaction]]:
    return {
        sender: list(txs) for sender, txs in
        groupby(sorted(filter(
            lambda t: t.Destination == ACCOUNT_ADDRESS,
            map(lambda t: Transaction(**t['tx']),
                await xrpl.asyncio.account.get_account_transactions(ACCOUNT_ADDRESS, CLIENT))
        ), key=lambda t: t.Account), key=lambda t: t.Account)
    }


if __name__ == '__main__':
    print('Hello from oracle!')
    print('Incoming payments to the test account:')
    pprint(asyncio.run(get_incoming_payments()))
