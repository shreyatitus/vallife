from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import get_db, init_db
from services.ai_matching import process_blood_request
import os

app = Flask(__name__, static_folder='../../lifelink_frontend/lifelink_frontend')
CORS(app)

init_db()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, phone, blood, password, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (data["name"], data["email"], data.get("phone", ""), data["blood"], data["password"], data.get("latitude", 0), data.get("longitude", 0))
        )
        conn.commit()
        return jsonify({"message": "Registration successful"})
    except Exception as e:
        return jsonify({"message": f"Registration failed: {str(e)}"})
    finally:
        cursor.close()
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (data["email"], data["password"]))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user:
        return jsonify({"status": "success", "user": {"id": user["id"], "name": user["name"], "email": user["email"]}})
    return jsonify({"status": "error", "message": "Invalid credentials"})

@app.route("/dashboard/<int:uid>", methods=["GET"])
def dashboard(uid):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT donations, points FROM users WHERE id=%s", (uid,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user:
        return jsonify({"donations": user["donations"], "points": user["points"], "status": "Eligible"})
    return jsonify({"donations": 0, "points": 0, "status": "Unknown"})

@app.route("/create-request", methods=["POST"])
def create_request():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO requests (patientName, blood, hospital, latitude, longitude) VALUES (%s, %s, %s, %s, %s)",
        (data["patientName"], data["blood"], data["hospital"], data.get("latitude", 0), data.get("longitude", 0))
    )
    conn.commit()
    request_id = cursor.lastrowid
    cursor.close()
    conn.close()
    
    result = process_blood_request(request_id, data["blood"], data.get("latitude", 0), data.get("longitude", 0), data["patientName"], data["hospital"])
    
    if result["status"] == "success":
        return jsonify({"message": f"Donor found: {result['donor']['name']} ({result['donor']['distance']} km away). Email sent to {result['donor']['email']}"})
    return jsonify({"message": result["message"]})

@app.route("/request-blood", methods=["POST"])
def request_blood():
    data = request.json
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name, points FROM users WHERE blood=%s LIMIT 1", (data["blood"],))
    donor = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if donor:
        return jsonify({"message": "Donor Found", "name": donor["name"], "points": donor["points"]})
    return jsonify({"message": "No donor found"})

@app.route("/get-requests", methods=["GET"])
def get_requests():
    user_id = request.args.get('user_id')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT blood FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    
    if user:
        cursor.execute("SELECT * FROM requests WHERE blood=%s AND status='pending' ORDER BY created_at DESC", (user['blood'],))
        requests = cursor.fetchall()
    else:
        requests = []
    
    cursor.close()
    conn.close()
    return jsonify({"requests": requests})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
