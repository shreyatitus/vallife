import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase (you'll need to add your credentials)
try:
    cred = credentials.Certificate("firebase-credentials.json")
    firebase_admin.initialize_app(cred)
except:
    # If credentials file doesn't exist, initialize without credentials for testing
    try:
        firebase_admin.initialize_app()
    except:
        pass

db = firestore.client()

def get_db():
    return db

def init_db():
    # Firebase doesn't require table creation
    pass
