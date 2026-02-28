from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✓ Firebase connected successfully!")
except Exception as e:
    print(f"✗ Firebase connection error: {e}")
    db = None

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "LifeLink API Running", "version": "1.0"})

@app.route("/ai-chat", methods=["POST", "OPTIONS"])
def ai_chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    data = request.json
    user_message = data.get("message", "")
    conversation_history = data.get("history", [])
    
    print(f"Received message: {user_message}")
    
    try:
        from services.groq_assistant import chat_with_assistant
        from services.ai_donor_matcher import process_blood_request_ai
        
        response = chat_with_assistant(user_message, conversation_history, db)
        
        print(f"AI Response preview: {response[:100]}...")
        
        if "BLOOD_REQUEST_COMPLETE" in response:
            print("Processing blood request...")
            try:
                from services.geocoding_service import get_coordinates
                
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                request_data = json.loads(json_str)
                
                print(f"Extracted data: {request_data}")
                
                location = request_data.get("location", "")
                if location:
                    print(f"Geocoding location: {location}")
                    coords = get_coordinates(location)
                    if coords:
                        request_data["latitude"] = coords["latitude"]
                        request_data["longitude"] = coords["longitude"]
                        print(f"✓ Geocoded {location} to {coords['latitude']}, {coords['longitude']}")
                    else:
                        request_data["latitude"] = 0
                        request_data["longitude"] = 0
                else:
                    request_data["latitude"] = 0
                    request_data["longitude"] = 0
                
                request_data["status"] = "pending"
                request_data["created_at"] = firestore.SERVER_TIMESTAMP
                
                request_ref = db.collection("requests").add(request_data)
                request_id = request_ref[1].id
                
                print(f"Request created with ID: {request_id}")
                
                result = process_blood_request_ai(db, request_id, request_data)
                
                if result["status"] == "success":
                    donor = result["matched_donor"]
                    response = f"""Blood Request Created Successfully!

Request Details:
- Patient: {request_data['patientName']}
- Blood Type: {request_data['blood']}
- Hospital: {request_data['hospital']}
- Location: {request_data.get('location', 'N/A')} ({request_data.get('latitude', 0)}, {request_data.get('longitude', 0)})

Matched Donor:
- Name: {donor['name']}
- Email: {donor['email']}
- Distance: {donor['distance']} km away
- Donations: {donor.get('points', 0)} points

✅ Email sent to {donor['email']}

Status: Waiting for donor response...
{len(result.get('all_donors', [])) - 1} backup donors available."""
                else:
                    response = f"No eligible donors found for {request_data['blood']} blood type."
                    
            except Exception as e:
                print(f"Error processing request: {e}")
                import traceback
                traceback.print_exc()
                response = f"Error processing request: {str(e)}"
        
        return jsonify({"response": response})
        
    except Exception as e:
        print(f"AI Chat Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"response": f"Error: {str(e)}"})

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
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        db.collection("users").add(user_data)
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
        
        users = db.collection("users").where("email", "==", data["email"]).where("password", "==", data["password"]).limit(1).stream()
        
        for user in users:
            user_data = user.to_dict()
            if user_data.get("status") != "approved":
                return jsonify({"status": "error", "message": "Account pending admin verification"})
            return jsonify({"status": "success", "user": {"id": user.id, "name": user_data["name"], "email": data["email"]}})
        
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
        users = db.collection("users").where("status", "==", "pending").stream()
        user_list = [dict(user.to_dict(), id=user.id) for user in users]
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
        user_ref = db.collection("users").document(data["user_id"])
        user_ref.update({"status": "approved"})
        return jsonify({"message": "User approved"})
    except Exception as e:
        print(f"Error approving user: {e}")
        return jsonify({"message": "Approval failed"}), 500

@app.route("/admin/reject-user", methods=["POST", "OPTIONS"])
def admin_reject_user():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        db.collection("users").document(request.json["user_id"]).delete()
        return jsonify({"message": "User rejected"})
    except Exception as e:
        print(f"Error rejecting user: {e}")
        return jsonify({"message": "Rejection failed"}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
    print("="*60)
    print("LifeLink Backend Starting...")
    print("Conversational AI Blood Request System")
    print("Server running on http://localhost:5000")
    print("="*60)
    app.run(debug=True, port=5000, use_reloader=False, host='0.0.0.0')
