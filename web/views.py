from flask import render_template

from connect_to_blockchain import connect
from web import app, login_manager
from web.models import *

contract_container = connect()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/renter/<renter_id>')
def renter_info(renter_id: int):
    user = User.query.get(renter_id)
    error, balance, tariff, name, transactions = [None] * 5
    if user is None:
        error = 'Пользователь не найден'
    elif not user.is_renter:
        error = 'Пользователь не является арендатором'
    else:
        balance = contract_container.getBalance(user.account)
        tariff = contract_container.getTariff(user.account)
        name = user.username
        transactions = [[], []]  # TODO: get last transactions
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
