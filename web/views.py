from flask import render_template, request
from flask_login import current_user

from connect_to_blockchain import contract_container, owner_account
from iter_day import time_to_update
from web import app, login_manager
from web.models import *
from brownie import history


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def home():
    user = User.query.get(current_user.get_id())
    error, balance, tariff, name, transactions, account = [None] * 6
    if user is None:
        error = 'Пользователь не найден'
    elif not user.is_renter:
        error = 'Пользователь не является арендатором'
    else:
        balance = contract_container.getBalance(user.account)
        tariff = contract_container.getTariff(user.account)
        name = user.username
        account = user.account
        transactions = history.filter(sender=account)
    return render_template('index.html', balance=balance if balance else 0,
                           tariff=tariff if tariff else 1, name=name,
                           transactions=enumerate(transactions if transactions else []),
                           next_upd='%d ч %d мин' %
                                    (time_to_update[0] // 3600, (time_to_update[0] // 60) % 60))


@app.route('/renter/<renter_id>', methods=['GET', 'POST'])
def renter_info(renter_id: int):
    user = User.query.get(renter_id)
    error, balance, tariff, name, transactions, account, msg = [None] * 7
    if user is None:
        error = 'Пользователь не найден'
    elif not user.is_renter:
        error = 'Пользователь не является арендатором'
    else:
        balance = contract_container.getBalance(user.account)
        tariff = contract_container.getTariff(user.account)
        name = user.username
        if request.method == 'POST':
            new_balance = int(request.form.get('balance'))
            new_tariff = int(request.form.get('tariff'))
            if new_balance != balance:
                contract_container.setBalance(user.account, new_balance, {'from': owner_account})
                balance = new_balance
                msg = 'Сохранено'
            if new_tariff != tariff:
                contract_container.set(user.account, new_tariff, {'from': owner_account})
                tariff = new_tariff
                msg = 'Сохранено'
    return render_template('renter.html', error=error, balance=balance,
                           tariff=tariff, name=name, msg=msg)


@app.route('/stats')
def stats():
    users = list(User.query.filter(User.is_renter))
    for user in users:
        user.balance = contract_container.getBalance(user.account)
        user.tariff = contract_container.getTariff(user.account)
    return render_template('stats.html', renters=users)


@app.route('/payments')
def payments():
    return render_template('payments.html')
