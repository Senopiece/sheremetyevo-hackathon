from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, TypeDecorator
from flask_login import UserMixin
from web import db

db.metadata.clear()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(120), unique=False)

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username
