from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db, init_db
from services.ai_matching import process_blood_request
from agents.orchestrator import AgentOrchestrator
from agents.nlp_agent import NLPAgent

app = Flask(__name__)
CORS(app)

init_db()

# Initialize AI agents
orchestrator = AgentOrchestrator()
nlp_agent = NLPAgent()

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
        "INSERT INTO requests (patientName, blood, hospital, latitude, longitude, created_by) VALUES (%s, %s, %s, %s, %s, %s)",
        (data["patientName"], data["blood"], data["hospital"], data.get("latitude", 0), data.get("longitude", 0), data.get("user_id"))
    )
    conn.commit()
    request_id = cursor.lastrowid
    cursor.close()
    conn.close()
    
    # Use AI agent orchestrator for intelligent processing
    result = orchestrator.process_blood_request(request_id, data)
    
    if result["status"] == "success":
        donor = result['primary_donor']
        return jsonify({
            "message": f"AI matched donor: {donor['name']} ({donor['distance']} km away)",
            "urgency": result['urgency'],
            "availability_score": donor['availability_score'],
            "backup_donors": result['backup_count'],
            "analysis": result['analysis']
        })
    return jsonify({"message": result["message"], "analysis": result.get('analysis', {})})

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

@app.route("/nlp-request", methods=["POST"])
def nlp_request():
    """Process natural language blood request"""
    data = request.json
    text = data.get("text", "")
    
    # Parse natural language
    parsed = nlp_agent.parse_natural_language_request(text)
    
    if not parsed.get("bloodType"):
        return jsonify({"error": "Could not determine blood type from request"})
    
    # Create request
    conn = get_db()
<<<<<<< HEAD
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO requests (patientName, blood, hospital, latitude, longitude, 
           urgency, natural_language_request) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (parsed["patientName"], parsed["bloodType"], parsed["hospital"], 
         data.get("latitude", 0), data.get("longitude", 0), parsed["urgency"], text)
    )
    conn.commit()
    request_id = cursor.lastrowid
=======
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT blood FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    
    if user:
        cursor.execute("""
            SELECT r.* FROM requests r
            LEFT JOIN notifications n ON r.id = n.request_id AND n.donor_id = %s
            WHERE r.blood=%s AND r.status='pending'
            ORDER BY r.created_at DESC
        """, (user_id, user['blood']))
        requests = cursor.fetchall()
    else:
        requests = []
    
>>>>>>> b44de129866b59920cd97066b83ed6c8e2b2569f
    cursor.close()
    conn.close()
    
    # Process with AI agents
    result = orchestrator.process_blood_request(request_id, {
        "patientName": parsed["patientName"],
        "blood": parsed["bloodType"],
        "hospital": parsed["hospital"],
        "latitude": data.get("latitude", 0),
        "longitude": data.get("longitude", 0)
    })
    
    return jsonify({"parsed": parsed, "result": result})

@app.route("/donor-response", methods=["POST"])
def donor_response():
    """Handle donor response and trigger learning"""
    data = request.json
    notification_id = data["notification_id"]
    response = data["response"]  # 'accepted' or 'declined'
    response_time = data.get("response_time", 300)
    
    # Update notification
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT donor_id FROM notifications WHERE id=%s", (notification_id,))
    notif = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if notif:
        # Learn from response
        orchestrator.matcher.update_donor_pattern(
            notif['donor_id'], 
            response_time, 
            response == 'accepted'
        )
        
        if response == 'declined':
            # Autonomous retry with next donor
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT request_id FROM notifications WHERE id=%s", (notification_id,))
            req = cursor.fetchone()
            cursor.close()
            
            if req:
                retry_result = orchestrator.autonomous_retry(req['request_id'])
                return jsonify({"message": "Response recorded, contacting next donor", "retry": retry_result})
    
    return jsonify({"message": "Response recorded"})

@app.route("/system-insights", methods=["GET"])
def system_insights():
    """Get AI-driven system insights"""
    insights = orchestrator.get_system_insights()
    return jsonify(insights)

@app.route("/autonomous-monitor", methods=["POST"])
def autonomous_monitor():
    """Trigger autonomous monitoring and actions"""
    results = orchestrator.run_autonomous_monitoring()
    return jsonify({"actions_taken": results})

@app.route("/accept-request", methods=["POST"])
def accept_request():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE requests SET status='accepted', matched_donor_id=%s WHERE id=%s", (data['donor_id'], data['request_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"message": "Request accepted! Awaiting admin verification."})

@app.route("/my-requests", methods=["GET"])
def my_requests():
    user_id = request.args.get('user_id')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM requests WHERE created_by=%s ORDER BY created_at DESC", (user_id,))
    requests = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"requests": requests})

@app.route("/admin-login", methods=["POST"])
def admin_login():
    data = request.json
    if data["username"] == "admin" and data["password"] == "admin123":
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid credentials"})

@app.route("/admin/accepted-requests", methods=["GET"])
def admin_accepted_requests():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM requests WHERE status='accepted' ORDER BY created_at DESC")
    requests = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"requests": requests})

@app.route("/admin/verify-request", methods=["POST"])
def admin_verify_request():
    data = request.json
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT matched_donor_id FROM requests WHERE id=%s", (data['request_id'],))
    req = cursor.fetchone()
    
    if req and req['matched_donor_id']:
        cursor.execute("UPDATE requests SET status='completed' WHERE id=%s", (data['request_id'],))
        cursor.execute("UPDATE users SET donations=donations+1, points=points+10 WHERE id=%s", (req['matched_donor_id'],))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Request verified! Donor awarded 10 points."})
    
    cursor.close()
    conn.close()
    return jsonify({"message": "Request not found"})

if __name__ == "__main__":
    print("🤖 LifeLink AI Agent System Starting...")
    print("✓ Coordinator Agent: Analyzes requests and makes strategic decisions")
    print("✓ Matcher Agent: Finds optimal donors with predictive scoring")
    print("✓ Communication Agent: Generates personalized messages")
    print("✓ Monitor Agent: Autonomous monitoring and retry logic")
    print("✓ NLP Agent: Natural language request processing")
    app.run(debug=True, port=5000)
