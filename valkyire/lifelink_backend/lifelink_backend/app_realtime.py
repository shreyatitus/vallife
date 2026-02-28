from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db as firebase_db
import json
import uuid

app = Flask(__name__)
CORS(app)

try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://lifelink-a1172-default-rtdb.firebaseio.com/'
    })
    db = firebase_db.reference()
    print("✓ Firebase Realtime Database connected successfully!")
except Exception as e:
    print(f"✗ Firebase connection error: {e}")
    db = None

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "LifeLink API Running", "version": "1.0"})

@app.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No data provided"}), 400
        
        age = int(data.get("age", 0))
        weight = float(data.get("weight", 0))
        height = float(data.get("height", 0))
        report_date = datetime.strptime(data.get("reportDate"), "%Y-%m-%d")
        days_old = (datetime.now() - report_date).days
        
        if age < 18 or age > 65:
            return jsonify({"message": "Age must be between 18 and 65"}), 400
        if weight < 50:
            return jsonify({"message": "Weight must be at least 50 kg"}), 400
        if height < 150:
            return jsonify({"message": "Height must be at least 150 cm"}), 400
        if days_old > 90:
            return jsonify({"message": "Blood test report must be within last 90 days"}), 400
        
        user_id = str(uuid.uuid4())
        user_data = {
            "name": data["name"],
            "email": data["email"],
            "phone": data.get("phone", ""),
            "age": age,
            "weight": weight,
            "height": height,
            "blood": data["blood"],
            "password": data["password"],
            "latitude": data.get("latitude", 0),
            "longitude": data.get("longitude", 0),
            "reportData": data.get("reportData"),
            "reportName": data.get("reportName"),
            "reportDate": data.get("reportDate"),
            "status": "pending",
            "donations": 0,
            "points": 0,
            "created_at": datetime.now().isoformat()
        }
        
        db.child("users").child(user_id).set(user_data)
        return jsonify({"message": "Registration submitted! You will receive an email once verified."})
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500

@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.json
        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"status": "error", "message": "Email and password required"}), 400
        
        users = db.child("users").get()
        if users:
            for user_id, user_data in users.items():
                if user_data.get("email") == data["email"] and user_data.get("password") == data["password"]:
                    if user_data.get("status") != "approved":
                        return jsonify({"status": "error", "message": "Account pending admin verification"})
                    return jsonify({"status": "success", "user": {"id": user_id, "name": user_data["name"], "email": data["email"]}})
        
        return jsonify({"status": "error", "message": "Invalid credentials"})
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"status": "error", "message": "Login failed"}), 500

@app.route("/admin-login", methods=["POST", "OPTIONS"])
def admin_login():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    data = request.json
    if data["username"] == "admin" and data["password"] == "admin123":
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid credentials"})

@app.route("/admin/pending-users", methods=["GET", "OPTIONS"])
def admin_pending_users():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        users = db.child("users").get()
        user_list = []
        if users:
            for user_id, user_data in users.items():
                if user_data.get("status") == "pending":
                    user_data["id"] = user_id
                    user_list.append(user_data)
        return jsonify({"users": user_list})
    except Exception as e:
        print(f"Error fetching pending users: {e}")
        return jsonify({"users": []}), 500

@app.route("/admin/approve-user", methods=["POST", "OPTIONS"])
def admin_approve_user():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.json
        user_id = data["user_id"]
        user_email = data.get("email")
        
        # Update user status
        db.child("users").child(user_id).update({"status": "approved"})
        
        # Send approval email
        if user_email:
            try:
                from services.email_service import send_email
                subject = "LifeLink - Registration Approved!"
                body = f"""Dear Donor,

Congratulations! Your registration with LifeLink has been approved.

You can now log in to your account and start saving lives by donating blood.

Thank you for being a hero!

Best regards,
LifeLink Team"""
                send_email(user_email, subject, body)
                print(f"Approval email sent to {user_email}")
            except Exception as email_error:
                print(f"Email sending failed: {email_error}")
        
        return jsonify({"message": "User approved and email sent"})
    except Exception as e:
        print(f"Error approving user: {e}")
        return jsonify({"message": "Approval failed"}), 500

@app.route("/admin/reject-user", methods=["POST", "OPTIONS"])
def admin_reject_user():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        db.child("users").child(request.json["user_id"]).delete()
        return jsonify({"message": "User rejected"})
    except Exception as e:
        print(f"Error rejecting user: {e}")
        return jsonify({"message": "Rejection failed"}), 500

@app.route("/create-request", methods=["POST", "OPTIONS"])
def create_request():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.json
        request_id = str(uuid.uuid4())
        request_data = {
            "patientName": data.get("patientName"),
            "blood": data.get("blood"),
            "hospital": data.get("hospital"),
            "location": data.get("location", ""),
            "latitude": data.get("latitude", 0),
            "longitude": data.get("longitude", 0),
            "userId": data.get("userId"),  # Store who created the request
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        db.child("requests").child(request_id).set(request_data)
        
        # Find and notify matching donor
        try:
            blood_type = request_data["blood"]
            print(f"Looking for donors with blood type: {blood_type}")
            users = db.child("users").get()
            eligible_donors = []
            
            if users:
                print(f"Found {len(users)} total users in database")
                for user_id, user_data in users.items():
                    user_blood = user_data.get("blood")
                    user_status = user_data.get("status")
                    print(f"User {user_data.get('name')}: blood={user_blood}, status={user_status}")
                    
                    if user_blood == blood_type and user_status == "approved":
                        eligible_donors.append({
                            "id": user_id,
                            "name": user_data.get("name"),
                            "email": user_data.get("email")
                        })
                        print(f"✓ Added {user_data.get('name')} as eligible donor")
            else:
                print("No users found in database")
            
            print(f"Total eligible donors found: {len(eligible_donors)}")
            
            if eligible_donors:
                # Notify first eligible donor
                donor = eligible_donors[0]
                print(f"Sending email to: {donor['email']}")
                from services.email_service import send_email
                subject = f"Urgent: Blood Donation Request - {blood_type} Type"
                body = f"""Dear {donor['name']},

A patient urgently needs your help!

Patient Name: {request_data['patientName']}
Blood Type Required: {blood_type}
Hospital: {request_data['hospital']}
Location: {request_data['location']}

You have been matched as an eligible donor.
Please respond as soon as possible.

Thank you for saving lives!

LifeLink Team"""
                send_email(donor['email'], subject, body)
                print(f"✓ Donor notification sent to {donor['email']}")
            else:
                print(f"✗ No eligible donors found for blood type {blood_type}")
        except Exception as e:
            print(f"Error notifying donor: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify({"message": "Blood request created successfully", "request_id": request_id})
    except Exception as e:
        print(f"Error creating request: {e}")
        return jsonify({"message": f"Request creation failed: {str(e)}"}), 500

@app.route("/my-requests", methods=["GET", "OPTIONS"])
def my_requests():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        user_id = request.args.get("userId")
        if not user_id:
            return jsonify({"requests": []})
        
        requests = db.child("requests").get()
        user_requests = []
        
        if requests:
            for req_id, req_data in requests.items():
                if req_data.get("userId") == user_id:
                    req_data["id"] = req_id
                    user_requests.append(req_data)
        
        return jsonify({"requests": user_requests})
    except Exception as e:
        print(f"Error fetching requests: {e}")
        return jsonify({"requests": []}), 500

@app.route("/available-requests", methods=["GET", "OPTIONS"])
def available_requests():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        user_id = request.args.get("userId")
        if not user_id:
            return jsonify({"requests": []})
        
        # Get user's blood type
        user_data = db.child("users").child(user_id).get()
        if not user_data:
            return jsonify({"requests": []})
        
        user_blood = user_data.get("blood")
        
        # Get all pending requests matching user's blood type
        requests = db.child("requests").get()
        available = []
        
        if requests:
            for req_id, req_data in requests.items():
                # Show requests that match user's blood type and are pending
                if req_data.get("blood") == user_blood and req_data.get("status") == "pending":
                    req_data["id"] = req_id
                    available.append(req_data)
        
        return jsonify({"requests": available})
    except Exception as e:
        print(f"Error fetching available requests: {e}")
        return jsonify({"requests": []}), 500

@app.route("/accept-request", methods=["POST", "OPTIONS"])
def accept_request():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.json
        request_id = data.get("request_id")
        donor_id = data.get("donor_id")
        
        # Update request status to accepted (waiting for admin verification)
        db.child("requests").child(request_id).update({
            "status": "accepted",
            "donorId": donor_id,
            "acceptedAt": datetime.now().isoformat()
        })
        
        # Get request details
        request_data = db.child("requests").child(request_id).get()
        
        # Get donor details
        donor_data = db.child("users").child(donor_id).get()
        
        # Send confirmation email to donor
        if donor_data and donor_data.get("email"):
            from services.email_service import send_email
            subject = "Blood Donation Request Accepted - Thank You!"
            body = f"""Dear {donor_data.get('name')},

Thank you for accepting the blood donation request!

Patient: {request_data.get('patientName')}
Blood Type: {request_data.get('blood')}
Hospital: {request_data.get('hospital')}
Location: {request_data.get('location')}

Please proceed to the hospital as soon as possible.
After donation, admin will verify and award you points.

You are a hero!

LifeLink Team"""
            send_email(donor_data.get('email'), subject, body)
        
        return jsonify({"message": "Request accepted! Check your email for details."})
    except Exception as e:
        print(f"Error accepting request: {e}")
        return jsonify({"message": "Failed to accept request"}), 500

@app.route("/admin/accepted-requests", methods=["GET", "OPTIONS"])
def admin_accepted_requests():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        requests = db.child("requests").get()
        accepted_list = []
        
        if requests:
            for req_id, req_data in requests.items():
                if req_data.get("status") == "accepted":
                    # Get donor details
                    donor_id = req_data.get("donorId")
                    if donor_id:
                        donor_data = db.child("users").child(donor_id).get()
                        if donor_data:
                            req_data["donorName"] = donor_data.get("name")
                            req_data["donorEmail"] = donor_data.get("email")
                    req_data["id"] = req_id
                    accepted_list.append(req_data)
        
        return jsonify({"requests": accepted_list})
    except Exception as e:
        print(f"Error fetching accepted requests: {e}")
        return jsonify({"requests": []}), 500

@app.route("/admin/verify-donation", methods=["POST", "OPTIONS"])
def admin_verify_donation():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.json
        request_id = data.get("request_id")
        
        # Get request details
        request_data = db.child("requests").child(request_id).get()
        donor_id = request_data.get("donorId")
        
        # Update request status to completed
        db.child("requests").child(request_id).update({
            "status": "completed",
            "completedAt": datetime.now().isoformat()
        })
        
        # Award points to donor
        donor_data = db.child("users").child(donor_id).get()
        current_points = donor_data.get("points", 0)
        current_donations = donor_data.get("donations", 0)
        
        new_points = current_points + 10  # 10 points per donation
        new_donations = current_donations + 1
        
        db.child("users").child(donor_id).update({
            "points": new_points,
            "donations": new_donations,
            "lastDonation": datetime.now().isoformat()
        })
        
        # Send congratulations email
        if donor_data.get("email"):
            from services.email_service import send_email
            subject = "Donation Verified - Points Awarded!"
            body = f"""Dear {donor_data.get('name')},

Thank you for completing your blood donation!

Donation Details:
- Patient: {request_data.get('patientName')}
- Blood Type: {request_data.get('blood')}
- Hospital: {request_data.get('hospital')}

Rewards:
- Points Earned: +10
- Total Points: {new_points}
- Total Donations: {new_donations}

You are a true hero! Thank you for saving lives.

LifeLink Team"""
            send_email(donor_data.get('email'), subject, body)
        
        return jsonify({"message": "Donation verified and points awarded!"})
    except Exception as e:
        print(f"Error verifying donation: {e}")
        return jsonify({"message": "Verification failed"}), 500

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

if __name__ == "__main__":
    print("="*60)
    print("LifeLink Backend Starting...")
    print("Using Firebase Realtime Database (No Billing Required)")
    print("Server running on http://localhost:5000")
    print("="*60)
    app.run(debug=True, port=5000, use_reloader=False, host='0.0.0.0')
