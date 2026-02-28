import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase connected")
    
    # Add test user
    test_user = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "test123",
        "phone": "1234567890",
        "age": 25,
        "weight": 60,
        "height": 170,
        "blood": "O+",
        "latitude": 0,
        "longitude": 0,
        "reportData": "",
        "reportName": "test-report.pdf",
        "reportDate": "2024-01-01",
        "status": "approved",
        "donations": 0,
        "points": 0,
        "created_at": firestore.SERVER_TIMESTAMP
    }
    
    db.collection("users").add(test_user)
    print("Test user added: test@test.com / test123")
    
except Exception as e:
    print(f"Error: {e}")
