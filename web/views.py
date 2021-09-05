from brownie.exceptions import VirtualMachineError
from flask import render_template, request, abort, make_response, redirect, jsonify
from flask_login import current_user, login_required, login_user, logout_user

from connect_to_blockchain import contract_container, get_account
from iter_day import time_to_update
from forms import RegisterForm, LoginForm
from web import app, login_manager, db
from web.models import *
from brownie import history


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.errorhandler(401)
def unauthorized(error):
    return make_response(render_template('renter.html', error=error), 401)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if db.session.query(User).filter(User.username == form.login.data).first():
            return render_template('register.html', form=form,
                                   message='Пользователь с таким логином уже существует',
                                   message_type='danger')
        if db.session.query(User).filter(User.account == form.account_address.data).first():
            return render_template('register.html', form=form,
                                   message='Пользователь с таким адресом аккаунта уже существует',
                                   message_type='danger')
        user = User()
        user.username = form.login.data
        user.account = form.account_address.data
        user.set_password(form.password.data)
        user.is_renter = True
        db.session.add(user)
        db.session.commit()
        return render_template('register.html', form=form,
                               message='Аккаунт успешно создан', message_type='success')
    return render_template('register.html', form=form)


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
    transactions = history.filter(sender=account)
    return render_template('index.html', balance=balance if balance else 0,
                           tariff=tariff if tariff else 1, name=name,
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
    for user in users:
        user.balance = contract_container.getBalance(user.account)
        user.tariff = contract_container.getTariff(user.account)
    return render_template('stats.html', renters=users)


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
