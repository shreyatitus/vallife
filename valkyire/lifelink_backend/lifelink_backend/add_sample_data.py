import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Sample users
users = [
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "age": 28,
        "weight": 70,
        "height": 175,
        "blood": "A+",
        "password": "password123",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "reportDate": "2024-11-15",
        "reportName": "blood_test.pdf",
        "reportData": "data:application/pdf;base64,sample",
        "status": "approved",
        "donations": 2,
        "points": 20,
        "lastDonation": None
    },
    {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "9876543210",
        "age": 32,
        "weight": 65,
        "height": 168,
        "blood": "O+",
        "password": "password123",
        "latitude": 12.9800,
        "longitude": 77.6000,
        "reportDate": "2024-12-01",
        "reportName": "blood_report.pdf",
        "reportData": "data:application/pdf;base64,sample",
        "status": "approved",
        "donations": 1,
        "points": 10,
        "lastDonation": None
    },
    {
        "name": "Mike Johnson",
        "email": "mike@example.com",
        "phone": "5551234567",
        "age": 25,
        "weight": 75,
        "height": 180,
        "blood": "B+",
        "password": "password123",
        "latitude": 12.9650,
        "longitude": 77.5850,
        "reportDate": "2024-11-20",
        "reportName": "test_report.pdf",
        "reportData": "data:application/pdf;base64,sample",
        "status": "approved",
        "donations": 0,
        "points": 0,
        "lastDonation": None
    },
    {
        "name": "Sarah Williams",
        "email": "sarah@example.com",
        "phone": "5559876543",
        "age": 30,
        "weight": 60,
        "height": 165,
        "blood": "A+",
        "password": "password123",
        "latitude": 12.9750,
        "longitude": 77.5900,
        "reportDate": "2024-12-05",
        "reportName": "blood_test_report.pdf",
        "reportData": "data:application/pdf;base64,sample",
        "status": "approved",
        "donations": 3,
        "points": 30,
        "lastDonation": None
    }
]

print("Adding sample users to Firebase...")
for user in users:
    db.collection("users").add(user)
    print(f"Added: {user['name']} - {user['blood']}")

print("\nSample data added successfully!")
print("You can now:")
print("1. Login with any user (email/password: password123)")
print("2. Create blood requests")
print("3. Test AI donor matching")
