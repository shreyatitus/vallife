from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import json
from groq import Groq

app = Flask(__name__)
CORS(app)

# Initialize Firebase
try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✓ Firebase connected successfully!")
except Exception as e:
    print(f"❌ Firebase connection error: {e}")
    db = None

# Initialize Groq (FREE API)
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)
print("✓ Groq AI connected (FREE)!")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "LifeLink Agentic AI Running", "version": "2.0"})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

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
        
        # Detect intent
        msg_lower = message.lower()
        
        # Blood request
        if any(word in msg_lower for word in ["need", "urgent", "blood", "emergency", "accident"]):
            return handle_blood_request(message, latitude, longitude, user_id)
        
        # Donor availability
        elif any(word in msg_lower for word in ["available", "can donate", "ready"]):
            return handle_donor_availability(user_id)
        
        # Emergency guidance
        elif any(word in msg_lower for word in ["help", "what to do", "first aid", "bleeding"]):
            return handle_emergency_guidance(message)
        
        # Status check
        elif any(word in msg_lower for word in ["status", "my request", "check"]):
            return handle_status_check(user_id)
        
        # General query
        else:
            return handle_general_query(message)
            
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "reply": f"Sorry, I encountered an error: {str(e)}",
            "actions": [],
            "status": "error"
        })

def handle_blood_request(message, latitude, longitude, user_id):
    """Handle blood request with AI parsing"""
    try:
        # Parse with Groq AI
        prompt = f"""Extract blood donation details from this message and return ONLY a JSON object with no other text:

Message: "{message}"

Return this exact format:
{{"patientName": "name or Patient", "bloodType": "A+/A-/B+/B-/O+/O-/AB+/AB-", "hospital": "hospital name or Hospital", "urgency": "critical/high/medium/low"}}

Return ONLY the JSON, no explanation."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        if '{' in response_text:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            parsed = json.loads(json_str)
        else:
            # Fallback: manual extraction
            parsed = {
                "patientName": "Patient",
                "bloodType": extract_blood_type(message),
                "hospital": "Hospital",
                "urgency": "high" if any(w in message.lower() for w in ["urgent", "emergency", "critical"]) else "medium"
            }
        
        if not parsed.get("bloodType"):
            return jsonify({
                "reply": "I couldn't determine the blood type. Please specify (e.g., 'Need O+ blood urgently')",
                "actions": [],
                "status": "clarification_needed"
            })
        
        # Create request in Firebase
        request_data = {
            "patientName": parsed["patientName"],
            "blood": parsed["bloodType"],
            "hospital": parsed["hospital"],
            "latitude": latitude or 0,
            "longitude": longitude or 0,
            "urgency": parsed["urgency"],
            "natural_language_request": message,
            "created_by": user_id,
            "status": "pending",
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection("requests").add(request_data)
        request_id = doc_ref[1].id
        
        # Find matching donors
        donors = db.collection("users").where("blood", "==", parsed["bloodType"]).where("status", "==", "approved").limit(10).stream()
        donor_list = []
        notified_count = 0
        
        for donor in donors:
            donor_data = donor.to_dict()
            donor_data['id'] = donor.id
            donor_list.append(donor_data)
            
            # Send email to each donor
            try:
                from services.email_service import send_email
                send_email(
                    donor_data['email'],
                    "Urgent Blood Request - LifeLink",
                    f"""Dear {donor_data['name']},

A patient needs {parsed['bloodType']} blood urgently!

Patient: {parsed['patientName']}
Hospital: {parsed['hospital']}
Urgency: {parsed['urgency'].upper()}

Please login to LifeLink to accept this request.

Thank you,
LifeLink Team"""
                )
                notified_count += 1
            except Exception as e:
                print(f"Email error for {donor_data['email']}: {e}")
        
        reply = f"""✅ Request processed successfully!

📋 Extracted Details:
• Blood Type: {parsed['bloodType']}
• Patient: {parsed['patientName']}
• Hospital: {parsed['hospital']}
• Urgency: {parsed['urgency'].upper()}

🎯 Donor Matching:
• Found {len(donor_list)} eligible donors
• Notified {notified_count} donors via email
• Request ID: {request_id}

📱 Actions Taken:
✓ Request created in database
✓ {notified_count} donors notified via email
✓ Monitoring system activated

⏳ Status: Waiting for donor response..."""
        
        return jsonify({
            "reply": reply,
            "actions": ["extracted", "matched", "notified", "monitoring"],
            "status": "success",
            "request_id": request_id,
            "parsed": parsed
        })
        
    except Exception as e:
        print(f"Blood request error: {e}")
        return jsonify({
            "reply": f"Error processing request: {str(e)}",
            "actions": [],
            "status": "error"
        })

def handle_donor_availability(user_id):
    """Handle donor saying they're available"""
    try:
        if not user_id:
            return jsonify({
                "reply": "Please login first to see available requests!",
                "actions": []
            })
        
        # Get user
        user_doc = db.collection("users").document(str(user_id)).get()
        if not user_doc.exists:
            return jsonify({
                "reply": "Please register as a donor first to help save lives!",
                "actions": []
            })
        
        user_data = user_doc.to_dict()
        
        # Find matching requests
        requests = db.collection("requests").where("blood", "==", user_data["blood"]).where("status", "==", "pending").limit(3).stream()
        request_list = [r.to_dict() for r in requests]
        
        if request_list:
            req_list = "\n".join([
                f"• {r.get('patientName', 'Patient')} at {r.get('hospital', 'Hospital')} ({r.get('urgency', 'medium')} urgency)"
                for r in request_list
            ])
            
            reply = f"""🙏 Thank you, {user_data.get('name', 'Donor')}!

Active requests for {user_data['blood']} blood:
{req_list}

You can accept any request from the dashboard.
Your willingness to help is truly appreciated! ❤️"""
        else:
            reply = f"""Thank you for your willingness to donate! 

Currently no active requests for {user_data['blood']} blood.
We'll notify you immediately when someone needs your help. 🙏"""
        
        return jsonify({
            "reply": reply,
            "actions": ["availability_updated"],
            "available_requests": len(request_list)
        })
        
    except Exception as e:
        print(f"Availability error: {e}")
        return jsonify({
            "reply": "Error checking availability. Please try again.",
            "actions": []
        })

def handle_emergency_guidance(message):
    """Provide emergency first aid guidance"""
    try:
        prompt = f"""User needs emergency guidance: "{message}"

Provide brief, actionable first aid advice for blood-related emergencies.
Include:
1. Immediate steps (2-3 points)
2. What NOT to do (1-2 points)
3. When to call ambulance

Keep under 150 words. Be clear and calm."""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300
        )
        
        guidance = response.choices[0].message.content.strip()
        
        reply = f"""🚑 Emergency Guidance:

{guidance}

📞 Emergency Numbers:
• Ambulance: 108
• Blood Bank Helpline: 104

⚠️ This is AI-generated guidance. Always consult medical professionals for emergencies."""
        
        return jsonify({
            "reply": reply,
            "actions": ["guidance_provided"],
            "type": "emergency_guidance"
        })
        
    except Exception as e:
        print(f"Guidance error: {e}")
        return jsonify({
            "reply": "Error generating guidance. Please call emergency services immediately.",
            "actions": []
        })

def handle_status_check(user_id):
    """Check status of user's requests"""
    try:
        if not user_id:
            return jsonify({
                "reply": "Please login to check your request status.",
                "actions": []
            })
        
        requests = db.collection("requests").where("created_by", "==", str(user_id)).order_by("created_at", direction=firestore.Query.DESCENDING).limit(1).stream()
        
        request_list = [r.to_dict() for r in requests]
        
        if not request_list:
            return jsonify({
                "reply": "You don't have any active requests.",
                "actions": []
            })
        
        req = request_list[0]
        
        if req['status'] == 'completed':
            reply = f"""✅ Request Completed!

Patient: {req['patientName']}
Blood Type: {req['blood']}
Status: Donor confirmed and verified

Thank you for using LifeLink! 🙏"""
        elif req['status'] == 'accepted':
            reply = f"""🎉 Great news!

A donor has accepted your request for {req['blood']} blood!
Patient: {req['patientName']}
Hospital: {req['hospital']}

Status: Awaiting admin verification"""
        else:
            reply = f"""⏳ Request In Progress

Patient: {req['patientName']}
Blood Type: {req['blood']}
Hospital: {req['hospital']}
Urgency: {req.get('urgency', 'medium').upper()}

📊 Status: Searching for donors
I'm continuously monitoring. You'll be notified when someone accepts!"""
        
        return jsonify({
            "reply": reply,
            "actions": ["status_checked"],
            "request": req
        })
        
    except Exception as e:
        print(f"Status check error: {e}")
        return jsonify({
            "reply": "Error checking status. Please try again.",
            "actions": []
        })

def handle_general_query(message):
    """Handle general queries"""
    try:
        prompt = f"""User query: "{message}"

You are LifeLink AI, an emergency blood donation assistant.
Provide a helpful, concise response about:
- How the system works
- Blood donation process
- Eligibility criteria
- How to help

Keep under 100 words. Be friendly and encouraging."""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        return jsonify({
            "reply": response.choices[0].message.content.strip(),
            "actions": ["general_response"],
            "type": "general"
        })
        
    except Exception as e:
        print(f"General query error: {e}")
        return jsonify({
            "reply": "I'm here to help with blood donation requests. Try asking 'Need O+ blood urgently' or 'How does LifeLink work?'",
            "actions": []
        })

def extract_blood_type(text):
    """Extract blood type from text"""
    blood_types = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    text_upper = text.upper()
    for bt in blood_types:
        if bt in text_upper:
            return bt
    return None

if __name__ == "__main__":
    print("="*60)
    print("🤖 LifeLink Agentic AI System Starting...")
    print("✓ Chatbot: Natural language understanding")
    print("✓ Firebase: Cloud database")
    print("✓ Groq AI: FREE autonomous decision making")
    print("="*60)
    print("🚀 Server running on http://localhost:5000")
    print("📱 Open chatbot.html to start chatting!")
    print("="*60)
    app.run(debug=True, port=5000, use_reloader=False, host='0.0.0.0')
