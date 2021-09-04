from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from decouple import config

import logging
from threading import Thread

from iter_day import iter_day
from constants import SECRET_KEY, DEBUG, DB_URI

app = Flask(__name__)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.config['SECRET_KEY'] = SECRET_KEY
app.debug = DEBUG

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from web.views import *

if __name__ == '__main__':
    thread = Thread(target=iter_day)
    thread.start()
    app.debug = config("DEBUG", cast=bool, default=False)
    app.run("0.0.0.0", port=8000)
