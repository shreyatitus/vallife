from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db, init_db
from agents.simple_orchestrator import SimpleAgentOrchestrator

app = Flask(__name__)
CORS(app)

init_db()

# Initialize AI Agent
agent = SimpleAgentOrchestrator()

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
    """
    User creates blood request → AI Agent activates
    Workflow: Filter → Cooldown → Distance → Rank → Notify → Retry
    """
    data = request.json
    
    # Store request in database
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
    
    # AI Agent processes request autonomously
    result = agent.process_blood_request(request_id, data)
    
    if result["status"] == "success":
        return jsonify({
            "message": f"✓ Donor found: {result['donor']['name']} ({result['donor']['distance']} km away)",
            "donor": result['donor'],
            "notification_id": result['notification_id'],
            "backup_donors": result['backup_donors_count']
        })
    
    return jsonify({
        "message": result["message"],
        "step_failed": result.get('step', 'unknown')
    })

@app.route("/donor-response", methods=["POST"])
def donor_response():
    """If declined → tries next (Autonomous retry)"""
    data = request.json
    notification_id = data["notification_id"]
    response = data["response"]  # 'accepted' or 'declined'
    
    result = agent.handle_donor_response(notification_id, response)
    
    return jsonify(result)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 LifeLink Agentic AI System")
    print("="*60)
    print("\nWorkflow:")
    print("  1. User creates blood request")
    print("  2. AI Agent activates")
    print("  3. Filters donors (blood group)")
    print("  4. Checks cooldown eligibility")
    print("  5. Calculates distance (Haversine)")
    print("  6. Ranks nearest valid donors")
    print("  7. Notifies top donor")
    print("  8. If declined → tries next")
    print("\n" + "="*60)
    print("Server starting on http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)
