import os
from decouple import config

SECRET_KEY = config('SECRET_KEY', default=os.urandom(32))
DEBUG = config('DEBUG', default=True, cast=bool)
DB_URI = config('DB_URI', default='sqlite:///db.sqlite3')

PROVIDER_URL = config('PROVIDER_URL', default='http://127.0.0.1:8545')
CONTRACT_ADDRESS = config('CONTRACT_ADDRESS', default=None)
OWNER_ADDRESS = config('OWNER_ADDRESS', default=None)
