from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from agents.chatbot_agent import ChatbotAgent
from agents.orchestrator import AgentOrchestrator

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Firebase
try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✓ Firebase connected successfully!")
except Exception as e:
    print(f"❌ Firebase connection error: {e}")
    db = None

# Initialize Agentic AI
orchestrator = AgentOrchestrator()
chatbot = ChatbotAgent(orchestrator)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "LifeLink Agentic AI Running", "version": "2.0"})

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    """Main agentic chatbot endpoint"""
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.json
        user_id = data.get("user_id")
        message = data.get("message", "")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Process with agentic chatbot
        response = chatbot.process_message(user_id, message, latitude, longitude)
        
        return jsonify(response)
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
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
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500

@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.json
        users = db.collection("users").where("email", "==", data["email"]).where("password", "==", data["password"]).limit(1).stream()
        
        for user in users:
            user_data = user.to_dict()
            if user_data.get("status") != "approved":
                return jsonify({"status": "error", "message": "Account pending admin verification"})
            return jsonify({"status": "success", "user": {"id": user.id, "name": user_data["name"], "email": data["email"]}})
        
        return jsonify({"status": "error", "message": "Invalid credentials"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Login failed"}), 500

@app.route("/dashboard/<user_id>", methods=["GET", "OPTIONS"])
def dashboard(user_id):
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return jsonify({
                "donations": user_data.get("donations", 0),
                "points": user_data.get("points", 0),
                "status": "Eligible"
            })
        
        return jsonify({"donations": 0, "points": 0, "status": "Unknown"})
    except Exception as e:
        return jsonify({"donations": 0, "points": 0, "status": "Unknown"}), 500

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
        return jsonify({"message": "Approval failed"}), 500

@app.route("/admin/reject-user", methods=["POST", "OPTIONS"])
def admin_reject_user():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        db.collection("users").document(request.json["user_id"]).delete()
        return jsonify({"message": "User rejected"})
    except Exception as e:
        return jsonify({"message": "Rejection failed"}), 500

if __name__ == "__main__":
    print("="*60)
    print("🤖 LifeLink Agentic AI System Starting...")
    print("✓ Chatbot Agent: Conversational interface")
    print("✓ Orchestrator: Multi-agent coordination")
    print("✓ Firebase: Cloud database")
    print("="*60)
    print("🚀 Server running on http://localhost:5000")
    print("📱 Open chatbot.html to start chatting!")
    print("="*60)
    app.run(debug=True, port=5000, use_reloader=False, host='0.0.0.0')
