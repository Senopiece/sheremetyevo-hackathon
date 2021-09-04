from web.models import *
from web import db

db.create_all()
u = User(username="admin", password="admin")
db.session.add(u)

db.session.commit()
