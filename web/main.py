from typing import List
from fastapi import FastAPI
import oracle

app = FastAPI()
id_to_account = {1: 'rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe'}


@app.get('/api/balance/{user_id}')
async def get_balance(user_id: int):
    data: dict[str, List[oracle.data_models.Transaction]] = await oracle.get_incoming_payments()
    return {'balance': sum(int(tx.Amount) for tx in data[id_to_account[user_id]])}
