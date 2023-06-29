from firebase_admin import credentials, firestore, initialize_app
from db import get_interactor

cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db_interactor = get_interactor()

# Random test code
