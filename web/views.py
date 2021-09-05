from datetime import datetime

from brownie.exceptions import VirtualMachineError
from flask import render_template, request, abort, make_response, redirect, jsonify
from flask_login import current_user, login_required, login_user, logout_user

from connect_to_blockchain import contract_container, get_account
from iter_day import time_to_update
from forms import RegisterForm, LoginForm
from web import app, login_manager, db
from web.models import *
from brownie import history
from brownie.network.state import Chain


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.errorhandler(401)
def unauthorized(error):
    return make_response(render_template('renter.html', error=error), 401)


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    whoami = db.session.query(User).get(current_user.get_id())
    form = RegisterForm()
    if form.validate_on_submit():
        if db.session.query(User).filter(User.username == form.login.data).first():
            return render_template('register.html', form=form,
                                   message='Пользователь с таким логином уже существует',
                                   message_type='danger', is_admin=not whoami.is_renter)
        if db.session.query(User).filter(User.account == form.account_address.data).first():
            return render_template('register.html', form=form,
                                   message='Пользователь с таким адресом аккаунта уже существует',
                                   message_type='danger', is_admin=not whoami.is_renter)
        user = User()
        user.username = form.login.data
        user.account = form.account_address.data
        user.set_password(form.password.data)
        user.is_renter = True
        db.session.add(user)
        db.session.commit()
        return render_template('register.html', form=form,
                               message='Аккаунт успешно создан', message_type='success',
                               is_admin=not whoami.is_renter)
    return render_template('register.html', form=form, is_admin=not whoami.is_renter)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/' if user.is_renter else '/admin')
        return render_template('login.html', message_type='danger',
                               message='Неправильный логин или пароль', form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


def get_transactions(account: str):
    transactions = history.filter(
        key=lambda k: "withdrawed" in k.events and k.events["withdrawed"][0]["user"] == account)
    transactions.extend(history.filter(key=lambda k: "payed" in k.events and k.events["payed"][0]["user"] == account))
    import locale
    locale.setlocale(locale.LC_TIME, ('RU', 'UTF8'))
    for trans in transactions:
        tr_time = datetime.fromtimestamp(trans.timestamp).strftime("%d %b\n%H:%M")
        setattr(trans, "time", tr_time)
    transactions.sort(key=lambda k: k.timestamp, reverse=True)
    return transactions


def get_total_payed(account: str, transactions=None):
    if transactions is None:
        transactions = get_transactions(account)
    return sum([tr.events["payed"]["value"] if "payed" in tr.events else 0 for tr in transactions])


def get_total_withdrawed(account: str, transactions=None):
    if transactions is None:
        transactions = get_transactions(account)
    return sum([tr.events["withdrawed"]["amount"] if "withdrawed" in tr.events else 0 for tr in transactions])


@app.route('/')
@login_required
def home():
    whoami = db.session.query(User).get(current_user.get_id())
    if not whoami.is_renter:
        return redirect('/admin')
    balance = contract_container.getBalance(whoami.account)
    tariff = contract_container.getTariff(whoami.account)
    name = whoami.username
    account = whoami.account
    transactions = get_transactions(account)
    total_withdrawed = get_total_withdrawed(account, transactions)
    total_payed = get_total_payed(account, transactions)

    return render_template('index.html', balance=balance if balance else 0,
                           tariff=tariff if tariff else 1, name=name,
                           total_withdrawed=total_withdrawed, total_payed=total_payed,
                           transactions=enumerate(transactions if transactions else []),
                           next_upd='%d ч %d мин' %
                                    (time_to_update[0] // 3600, (time_to_update[0] // 60) % 60))


@app.route('/renter/<renter_id>', methods=['GET', 'POST'])
@login_required
def renter_info(renter_id: int):
    whoami = db.session.query(User).get(current_user.get_id())
    user = db.session.query(User).get(renter_id)
    error, balance, tariff, name, transactions, account, msg = [None] * 7
    if whoami is None or whoami.is_renter:
        abort(401, 'Доступ запрещён')
    elif user is None:
        error = 'Пользователь не найден'
    elif not user.is_renter:
        error = 'Пользователь не является арендатором'
    else:
        balance = contract_container.getBalance(user.account)
        tariff = contract_container.getTariff(user.account)
        name = user.username
        if request.method == 'POST':
            if request.form.get('delete'):
                db.session.delete(user)
                db.session.commit()
                return redirect('/admin')
            else:
                new_tariff = int(request.form.get('tariff'))
                if new_tariff != tariff:
                    contract_container.set(user.account, new_tariff,
                                           {'from': get_account(user.account)})
                    tariff = new_tariff
                    msg = 'Сохранено'
    return render_template('renter.html', error=error, balance=balance,
                           tariff=tariff, name=name, msg=msg)


@app.route('/admin')
@login_required
def stats():
    whoami = db.session.query(User).get(current_user.get_id())
    if whoami is None or whoami.is_renter:
        abort(401, 'Доступ запрещён')
    users = list(db.session.query(User).filter(User.is_renter))
    total_tariff = 0
    for user in users:
        user.balance = contract_container.getBalance(user.account)
        user.tariff = contract_container.getTariff(user.account)
        total_tariff += user.tariff
        setattr(user, "total_payed", get_total_payed(user.account))
    return render_template('stats.html', renters=users, is_admin=not whoami.is_renter, total_tariff=total_tariff)


@app.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    metamask_addr = request.json["metamask_addr"]
    amount = request.json["amount"]

    whoami = db.session.query(User).get(current_user.get_id())
    if whoami is None:
        abort(401, 'Доступ запрещён')
    try:
        res = contract_container.withdraw(whoami.account, metamask_addr, amount)
    except VirtualMachineError as e:
        return jsonify({'status': "Ошибка во время транзакции. Доп. инфа: " + str(e.revert_msg)})
    return jsonify({'status': "Пополение прошло успешно. Доп. инфа: " + str(res)})


@app.route('/buy', methods=['POST'])
@login_required
def buy():
    chain = Chain()
    tx_hash = request.json["tx_hash"]

    whoami = db.session.query(User).get(current_user.get_id())
    if whoami is None:
        abort(401, 'Доступ запрещён')
    history._add_tx(chain.get_transaction(tx_hash))
    return 200


@app.route('/user-address')
@login_required
def get_user_addr():
    whoami = db.session.query(User).get(current_user.get_id())
    if whoami is None:
        abort(401, 'Доступ запрещён')
    return jsonify({'address': whoami.account})


@app.route('/contract-address')
@login_required
def get_contract_addr():
    return jsonify({'address': contract_container.address})
