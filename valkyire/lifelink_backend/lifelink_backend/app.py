from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db, init_db
from services.ai_matching import process_blood_request
from agents.orchestrator import AgentOrchestrator
from agents.nlp_agent import NLPAgent
from agents.chatbot_agent import ChatbotAgent
from services.auto_escalation_service import AutoEscalationService
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

init_db()

orchestrator = AgentOrchestrator()
nlp_agent = NLPAgent()
chatbot = ChatbotAgent(orchestrator)
escalation_service = AutoEscalationService(orchestrator)

# Start autonomous monitoring
escalation_service.start_monitoring()

@app.route("/register", methods=["POST"])
def register():
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
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, phone, age, weight, height, blood, password, latitude, longitude, reportData, reportName, reportDate, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')",
            (data["name"], data["email"], data.get("phone", ""), age, weight, height, data["blood"], data["password"], data.get("latitude", 0), data.get("longitude", 0), data.get("reportData"), data.get("reportName"), data.get("reportDate"))
        )
        conn.commit()
        return jsonify({"message": "Registration submitted! You will receive an email once verified."})
    except Exception as e:
        return jsonify({"message": f"Registration failed: {str(e)}"}), 400
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
        if user['status'] != 'approved':
            return jsonify({"status": "error", "message": "Account pending admin verification"})
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
    data = request.json
    text = data.get("text", "")
    
    parsed = nlp_agent.parse_natural_language_request(text)
    
    if not parsed.get("bloodType"):
        return jsonify({"error": "Could not determine blood type from request"})
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO requests (patientName, blood, hospital, latitude, longitude, 
           urgency, natural_language_request) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (parsed["patientName"], parsed["bloodType"], parsed["hospital"], 
         data.get("latitude", 0), data.get("longitude", 0), parsed["urgency"], text)
    )
    conn.commit()
    request_id = cursor.lastrowid
    cursor.close()
    conn.close()
    
    result = orchestrator.process_blood_request(request_id, {
        "patientName": parsed["patientName"],
        "blood": parsed["bloodType"],
        "hospital": parsed["hospital"],
        "latitude": data.get("latitude", 0),
        "longitude": data.get("longitude", 0)
    })
    
    return jsonify({"parsed": parsed, "result": result})

@app.route("/get-requests", methods=["GET"])
def get_requests():
    user_id = request.args.get('user_id')
    conn = get_db()
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
    
    cursor.close()
    conn.close()
    return jsonify({"requests": requests})

@app.route("/donor-response", methods=["POST"])
def donor_response():
    data = request.json
    notification_id = data["notification_id"]
    response = data["response"]
    response_time = data.get("response_time", 300)
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT donor_id FROM notifications WHERE id=%s", (notification_id,))
    notif = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if notif:
        orchestrator.matcher.update_donor_pattern(
            notif['donor_id'], 
            response_time, 
            response == 'accepted'
        )
        
        if response == 'declined':
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
    insights = orchestrator.get_system_insights()
    return jsonify(insights)

@app.route("/autonomous-monitor", methods=["POST"])
def autonomous_monitor():
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

@app.route("/admin/pending-users", methods=["GET"])
def admin_pending_users():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, phone, age, weight, height, blood, reportData, reportName, reportDate FROM users WHERE status='pending' ORDER BY created_at DESC")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"users": users})

@app.route("/admin/approve-user", methods=["POST"])
def admin_approve_user():
    data = request.json
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT email, name FROM users WHERE id=%s", (data['user_id'],))
    user = cursor.fetchone()
    
    cursor.execute("UPDATE users SET status='approved' WHERE id=%s", (data['user_id'],))
    conn.commit()
    cursor.close()
    conn.close()
    
    if user:
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

@app.route("/admin/reject-user", methods=["POST"])
def admin_reject_user():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (data['user_id'],))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User registration rejected"})

@app.route("/chat", methods=["POST"])
def chat():
    """Main chatbot endpoint - handles all conversational interactions"""
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message", "")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    # Process message with chatbot agent
    response = chatbot.process_message(user_id, message, latitude, longitude)
    
    return jsonify(response)

@app.route("/escalation-stats", methods=["GET"])
def escalation_stats():
    """Get auto-escalation statistics"""
    stats = escalation_service.get_escalation_stats()
    return jsonify({"stats": stats})

if __name__ == "__main__":
    print("🤖 LifeLink Agentic AI System Starting...")
    print("✓ Coordinator Agent: Analyzes requests and makes strategic decisions")
    print("✓ Matcher Agent: Finds optimal donors with predictive scoring")
    print("✓ Communication Agent: Generates personalized messages")
    print("✓ Monitor Agent: Autonomous monitoring and retry logic")
    print("✓ NLP Agent: Natural language request processing")
    print("✓ Chatbot Agent: Conversational interface with autonomous actions")
    print("✓ Auto-Escalation: Background monitoring every 5 minutes")
    print("\n🚀 System ready! Chatbot endpoint: POST /chat")
    app.run(debug=True, port=5000)
