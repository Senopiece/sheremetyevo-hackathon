from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, TypeDecorator, Boolean
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from web import db

db.metadata.clear()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    hashed_password = Column(String(), unique=False)
    is_renter = Column(Boolean())
    account = Column(String(42))

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
