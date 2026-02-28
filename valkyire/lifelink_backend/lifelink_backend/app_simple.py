from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory storage for testing
pending_users = {}
approved_users = {}
user_id_counter = 1

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "LifeLink API Running", "version": "1.0"})

@app.route("/register", methods=["POST"])
def register():
    global user_id_counter
    data = request.json
    
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
    
    pending_users[user_id_counter] = {
        "id": user_id_counter,
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
        "status": "pending"
    }
    user_id_counter += 1
    
    return jsonify({"message": "Registration submitted! You will receive an email once verified."})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    for user in approved_users.values():
        if user["email"] == email and user["password"] == password:
            return jsonify({"status": "success", "user": {"id": user["id"], "name": user["name"], "email": email}})
    
    for user in pending_users.values():
        if user["email"] == email:
            return jsonify({"status": "error", "message": "Account pending admin verification"})
    
    return jsonify({"status": "error", "message": "Invalid credentials"})

@app.route("/dashboard/<int:uid>", methods=["GET"])
def dashboard(uid):
    for user in approved_users.values():
        if user["id"] == uid:
            return jsonify({
                "donations": user.get("donations", 0),
                "points": user.get("points", 0),
                "status": "Eligible"
            })
    return jsonify({"donations": 0, "points": 0, "status": "Unknown"})

@app.route("/admin-login", methods=["POST"])
def admin_login():
    data = request.json
    if data["username"] == "admin" and data["password"] == "admin123":
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid credentials"})

@app.route("/admin/pending-users", methods=["GET"])
def admin_pending_users():
    return jsonify({"users": list(pending_users.values())})

@app.route("/admin/approve-user", methods=["POST"])
def admin_approve_user():
    data = request.json
    user_id = data["user_id"]
    
    if user_id in pending_users:
        user = pending_users[user_id]
        user["status"] = "approved"
        user["donations"] = 0
        user["points"] = 0
        approved_users[user_id] = user
        del pending_users[user_id]
        
        try:
            from services.email_service import send_email
            send_email(
                user['email'], 
                "LifeLink Account Approved", 
                f"Dear {user['name']},\n\nYour LifeLink donor account has been verified and approved! You can now login and start saving lives.\n\nThank you for joining LifeLink.\n\nBest regards,\nLifeLink Team"
            )
        except Exception as e:
            print(f"Email error: {e}")
        
        return jsonify({"message": "User approved and notified via email"})
    
    return jsonify({"message": "User not found"})

@app.route("/admin/reject-user", methods=["POST"])
def admin_reject_user():
    data = request.json
    user_id = data["user_id"]
    
    if user_id in pending_users:
        del pending_users[user_id]
        return jsonify({"message": "User registration rejected"})
    
    return jsonify({"message": "User not found"})

@app.route("/create-request", methods=["POST"])
def create_request():
    data = request.json
    return jsonify({"message": f"Blood request created for {data.get('patientName', 'patient')}"})

@app.route("/get-requests", methods=["GET"])
def get_requests():
    return jsonify({"requests": []})

@app.route("/my-requests", methods=["GET"])
def my_requests():
    return jsonify({"requests": []})

@app.route("/accept-request", methods=["POST"])
def accept_request():
    return jsonify({"message": "Request accepted"})

@app.route("/admin/accepted-requests", methods=["GET"])
def admin_accepted_requests():
    return jsonify({"requests": []})

@app.route("/admin/verify-request", methods=["POST"])
def admin_verify_request():
    return jsonify({"message": "Request verified"})

if __name__ == "__main__":
    print("LifeLink Backend Starting (In-Memory Mode)...")
    print("Registration with validation")
    print("Admin verification system")
    print("Email notifications")
    print("Server running on http://localhost:5000")
    app.run(debug=True, port=5000)
