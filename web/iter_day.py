import time

from connect_to_blockchain import contract_container, owner_account


def iter_day():
    while True:
        time.sleep(24 * 3600)
        contract_container.iterDay({'from': owner_account})
        print('Тарифы вычтены')
