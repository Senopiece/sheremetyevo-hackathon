from flask import render_template
from flask_login import current_user

from connect_to_blockchain import contract_container
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
    return render_template('index.html', balance=balance, tariff=tariff, name=name,
                           transactions=enumerate(transactions))


@app.route('/renter/<renter_id>')
def renter_info(renter_id: int):
    user = User.query.get(renter_id)
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
    return render_template('renter.html', msg=error, balance=balance, tariff=tariff, name=name,
                           transactions=enumerate(transactions))


@app.route('/renters')
def renters():
    pass


@app.route('/stats')
def stats():
    return render_template('stats.html')


@app.route('/payments')
def payments():
    return render_template('payments.html')
