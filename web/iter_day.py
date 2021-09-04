import time

from connect_to_blockchain import contract_container, owner_account

time_to_update = [24 * 3600]


def iter_day():
    global time_to_update
    while True:
        time.sleep(1)
        time_to_update[0] -= 1
        if time_to_update[0] == 0:
            contract_container.iterDay({'from': owner_account})
            print('Тарифы вычтены')
            time_to_update[0] = 24 * 3600
