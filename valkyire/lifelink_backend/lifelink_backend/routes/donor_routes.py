from flask import Blueprint, request, jsonify
from models.donor_model import Donor

donor_bp = Blueprint("donor_bp", __name__)

donors_list = []
users_db = {}
pending_users = {}
user_id_counter = 1

@donor_bp.route("/register", methods=["POST"])
def register_donor():
    global user_id_counter
    data = request.json

    pending_users[user_id_counter] = {
        "id": user_id_counter,
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"],
        "age": data["age"],
        "weight": data["weight"],
        "height": data["height"],
        "blood": data["blood"],
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "password": data["password"],
        "reportData": data["reportData"],
        "reportName": data["reportName"]
    }
    user_id_counter += 1

    return jsonify({"message": "Registration submitted! Wait for admin verification."})

@donor_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if email in users_db and users_db[email]["password"] == password:
        return jsonify({"status": "success", "user": {"id": users_db[email]["id"], "name": users_db[email]["name"], "email": email}})
    
    for user in pending_users.values():
        if user["email"] == email:
            return jsonify({"status": "error", "message": "Account pending verification"})
    
    return jsonify({"status": "error", "message": "Invalid credentials"})

@donor_bp.route("/dashboard/<int:user_id>", methods=["GET"])
def get_dashboard(user_id):
    for email, user in users_db.items():
        if user["id"] == user_id:
            return jsonify({
                "donations": user["donations"],
                "points": user["points"],
                "status": "Eligible"
            })
    return jsonify({"donations": 0, "points": 0, "status": "Not Found"})

@donor_bp.route("/create-request", methods=["POST"])
def create_request():
    data = request.json
    return jsonify({"message": f"Blood request created for {data['patientName']}"})

@donor_bp.route("/admin/pending-users", methods=["GET"])
def get_pending_users():
    return jsonify({"users": list(pending_users.values())})

@donor_bp.route("/admin/approve-user", methods=["POST"])
def approve_user():
    data = request.json
    user_id = data["user_id"]
    email = data["email"]
    
    if user_id in pending_users:
        user = pending_users[user_id]
        donor = Donor(user["name"], user["blood"], user["latitude"], user["longitude"])
        donors_list.append(donor)
        
        users_db[email] = {
            "id": user["id"],
            "password": user["password"],
            "name": user["name"],
            "blood": user["blood"],
            "donations": 0,
            "points": 0
        }
        del pending_users[user_id]
        return jsonify({"message": "User approved successfully"})
    
    return jsonify({"message": "User not found"})

@donor_bp.route("/admin/reject-user", methods=["POST"])
def reject_user():
    data = request.json
    user_id = data["user_id"]
    
    if user_id in pending_users:
        del pending_users[user_id]
        return jsonify({"message": "User rejected"})
    
    return jsonify({"message": "User not found"})
