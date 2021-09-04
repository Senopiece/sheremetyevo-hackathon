from flask import render_template

from web import app, login_manager
from web.models import *


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/renter/<renter_id>')
def renter_info(renter_id: int):
    return render_template("renter.html")


@app.route('/stats')
def stats():
    return render_template("stats.html")


@app.route('/payments')
def payments():
    return render_template("payments.html")
