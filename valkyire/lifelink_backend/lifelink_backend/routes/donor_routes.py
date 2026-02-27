from flask import Blueprint, request, jsonify
from models.donor_model import Donor

donor_bp = Blueprint("donor_bp", __name__)

donors_list = []
users_db = {}
user_id_counter = 1

@donor_bp.route("/register", methods=["POST"])
def register_donor():
    global user_id_counter
    data = request.json

    donor = Donor(
        data["name"],
        data["blood"],
        0.0,
        0.0
    )

    donors_list.append(donor)
    users_db[data["email"]] = {
        "id": user_id_counter,
        "password": data["password"], 
        "name": data["name"], 
        "blood": data["blood"],
        "donations": 0,
        "points": 0
    }
    user_id_counter += 1

    return jsonify({"message": "Donor registered successfully"})

@donor_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if email in users_db and users_db[email]["password"] == password:
        return jsonify({"status": "success", "user": {"id": users_db[email]["id"], "name": users_db[email]["name"], "email": email}})
    
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