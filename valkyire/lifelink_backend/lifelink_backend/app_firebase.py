from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase connected successfully!")
except Exception as e:
    print(f"Firebase connection error: {e}")
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

Email sent to {donor['email']}

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
        user_data = user_ref.get().to_dict()
        user_ref.update({"status": "approved"})
        
        if user_data:
            try:
                from services.email_service import send_email
                send_email(
                    user_data['email'], 
                    "LifeLink Account Approved", 
                    f"Dear {user_data['name']},\n\nYour LifeLink donor account has been verified and approved! You can now login and start saving lives.\n\nThank you for joining LifeLink.\n\nBest regards,\nLifeLink Team"
                )
            except Exception as e:
                print(f"Email error: {e}")
        
        return jsonify({"message": "User approved and notified via email"})
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

@app.route("/admin/accepted-requests", methods=["GET", "OPTIONS"])
def admin_accepted_requests():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        requests = db.collection("requests").where("status", "==", "accepted").stream()
        request_list = [dict(req.to_dict(), id=req.id) for req in requests]
        return jsonify({"requests": request_list})
    except Exception as e:
        print(f"Error fetching accepted requests: {e}")
        return jsonify({"requests": []}), 500

@app.route("/admin/verify-request", methods=["POST", "OPTIONS"])
def admin_verify_request():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.json
        print(f"Verify request data: {data}")
        
        if not data or not data.get("request_id"):
            return jsonify({"message": "Missing request_id"}), 400
        
        request_ref = db.collection("requests").document(data["request_id"])
        request_doc = request_ref.get()
        
        if not request_doc.exists:
            return jsonify({"message": "Request not found"}), 404
        
        request_data = request_doc.to_dict()
        print(f"Request data: {request_data}")
        
        if not request_data.get("matched_donor_id"):
            return jsonify({"message": "No matched donor found"}), 400
        
        # Update request status
        request_ref.update({"status": "completed"})
        print(f"Request {data['request_id']} marked as completed")
        
        # Update donor points
        donor_id = request_data["matched_donor_id"]
        donor_ref = db.collection("users").document(donor_id)
        donor_doc = donor_ref.get()
        
        if donor_doc.exists:
            donor_data = donor_doc.to_dict()
            old_donations = donor_data.get("donations", 0)
            old_points = donor_data.get("points", 0)
            
            donor_ref.update({
                "donations": old_donations + 1,
                "points": old_points + 10
            })
            print(f"Donor {donor_id} updated: donations {old_donations} -> {old_donations + 1}, points {old_points} -> {old_points + 10}")
            
            return jsonify({"message": f"Request verified! Donor awarded 10 points (Total: {old_points + 10})."})
        else:
            return jsonify({"message": "Donor not found"}), 404
        
    except Exception as e:
        print(f"Error verifying request: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"Verification failed: {str(e)}"}), 500

@app.route("/accept-request", methods=["POST", "OPTIONS"])
def accept_request():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.json
        donor_id = data["donor_id"]
        
        # Check cooldown period
        donor_ref = db.collection("users").document(donor_id)
        donor_doc = donor_ref.get()
        
        if donor_doc.exists:
            donor_data = donor_doc.to_dict()
            last_donation = donor_data.get("lastDonationDate")
            
            if last_donation:
                from datetime import datetime, timedelta
                if isinstance(last_donation, str):
                    last_donation = datetime.fromisoformat(last_donation)
                elif hasattr(last_donation, 'timestamp'):
                    last_donation = last_donation
                    
                days_since = (datetime.now() - last_donation).days if isinstance(last_donation, datetime) else 57
                
                if days_since < 56:
                    return jsonify({"message": f"You must wait {56 - days_since} more days before donating again."}), 400
        
        request_ref = db.collection("requests").document(data["request_id"])
        request_data = request_ref.get().to_dict()
        
        donor_data = donor_doc.to_dict()
        
        # Update request and set cooldown
        request_ref.update({
            "status": "accepted",
            "matched_donor_id": donor_id,
            "donorName": donor_data.get("name", "Unknown"),
            "donorEmail": donor_data.get("email", "N/A"),
            "acceptedAt": firestore.SERVER_TIMESTAMP
        })
        
        donor_ref.update({
            "lastDonationDate": firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"message": "Request accepted! Awaiting admin verification."})
    except Exception as e:
        print(f"Error accepting request: {e}")
        return jsonify({"message": "Failed to accept request"}), 500

@app.route("/available-requests", methods=["GET", "OPTIONS"])
def available_requests():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        user_id = request.args.get("userId")
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({"requests": []})
        
        user_data = user_doc.to_dict()
        
        # Check cooldown
        last_donation = user_data.get("lastDonationDate")
        if last_donation:
            from datetime import datetime
            if hasattr(last_donation, 'timestamp'):
                last_donation_dt = datetime.fromtimestamp(last_donation.timestamp())
            else:
                last_donation_dt = datetime.now()
            
            days_since = (datetime.now() - last_donation_dt).days
            if days_since < 56:
                return jsonify({
                    "requests": [],
                    "cooldown": True,
                    "daysRemaining": 56 - days_since,
                    "message": f"You are in cooldown period. {56 - days_since} days remaining."
                })
        
        requests = db.collection("requests").where("blood", "==", user_data["blood"]).where("status", "==", "pending").stream()
        request_list = [dict(req.to_dict(), id=req.id) for req in requests]
        return jsonify({"requests": request_list, "cooldown": False})
        
    except Exception as e:
        print(f"Error fetching available requests: {e}")
        return jsonify({"requests": []}), 500

@app.route("/create-request", methods=["POST", "OPTIONS"])
def create_request():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.json
        request_data = {
            "patientName": data["patientName"],
            "blood": data["blood"],
            "hospital": data["hospital"],
            "latitude": data.get("latitude", 0),
            "longitude": data.get("longitude", 0),
            "status": "pending",
            "created_by": data.get("userId"),
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        db.collection("requests").add(request_data)
        
        # Find eligible donors (not in cooldown)
        from datetime import datetime, timedelta
        all_donors = db.collection("users").where("blood", "==", data["blood"]).where("status", "==", "approved").stream()
        
        notified_count = 0
        for donor in all_donors:
            donor_data = donor.to_dict()
            
            # Check cooldown
            last_donation = donor_data.get("lastDonationDate")
            if last_donation:
                if hasattr(last_donation, 'timestamp'):
                    last_donation_dt = datetime.fromtimestamp(last_donation.timestamp())
                    days_since = (datetime.now() - last_donation_dt).days
                    if days_since < 56:
                        continue
            
            try:
                from services.email_service import send_email
                send_email(
                    donor_data['email'],
                    "Urgent Blood Request - LifeLink",
                    f"Dear {donor_data['name']},\n\nA patient needs {data['blood']} blood urgently!\n\nPatient: {data['patientName']}\nHospital: {data['hospital']}\n\nPlease login to LifeLink to accept this request.\n\nThank you,\nLifeLink Team"
                )
                notified_count += 1
            except Exception as e:
                print(f"Email error for {donor_data['email']}: {e}")
        
        return jsonify({"message": f"Blood request created! {notified_count} eligible donors notified."})
    except Exception as e:
        print(f"Error creating request: {e}")
        return jsonify({"message": f"Failed to create request: {str(e)}"}), 500

@app.route("/dashboard/<user_id>", methods=["GET", "OPTIONS"])
def dashboard(user_id):
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        print(f"Dashboard request for user: {user_id}")
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            donations = user_data.get("donations", 0)
            points = user_data.get("points", 0)
            print(f"User {user_id} stats: donations={donations}, points={points}")
            
            return jsonify({
                "donations": donations,
                "points": points,
                "status": "Eligible"
            })
        
        print(f"User {user_id} not found")
        return jsonify({"donations": 0, "points": 0, "status": "Unknown"})
    except Exception as e:
        print(f"Error fetching dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"donations": 0, "points": 0, "status": "Unknown"}), 500

@app.route("/my-requests", methods=["GET", "OPTIONS"])
def my_requests():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        user_id = request.args.get("userId")
        requests = db.collection("requests").where("created_by", "==", user_id).stream()
        request_list = [dict(req.to_dict(), id=req.id) for req in requests]
        return jsonify({"requests": request_list})
    except Exception as e:
        print(f"Error fetching my requests: {e}")
        return jsonify({"requests": []}), 500

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    """Agentic chatbot endpoint - integrates with existing system"""
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        from groq import Groq
        groq_client = Groq(api_key="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")
        
        data = request.json
        user_id = data.get("user_id")
        message = data.get("message", "")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        msg_lower = message.lower()
        
        # Blood request
        if any(word in msg_lower for word in ["need", "urgent", "blood", "emergency", "accident"]):
            # Parse with AI
            prompt = f"""Extract blood donation details from: "{message}"
Return JSON: {{"patientName": "name or Patient", "bloodType": "A+/A-/B+/B-/O+/O-/AB+/AB-", "hospital": "hospital or Hospital", "urgency": "critical/high/medium/low"}}
Return ONLY JSON."""
            
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=150
            )
            
            response_text = response.choices[0].message.content.strip()
            
            if '{' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                parsed = json.loads(json_str)
            else:
                blood_types = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
                text_upper = message.upper()
                blood_type = None
                for bt in blood_types:
                    if bt in text_upper:
                        blood_type = bt
                        break
                
                parsed = {
                    "patientName": "Patient",
                    "bloodType": blood_type,
                    "hospital": "Hospital",
                    "urgency": "high" if any(w in msg_lower for w in ["urgent", "emergency", "critical"]) else "medium"
                }
            
            if not parsed.get("bloodType"):
                return jsonify({
                    "reply": "I couldn't determine the blood type. Please specify (e.g., 'Need O+ blood urgently')",
                    "actions": [],
                    "status": "clarification_needed"
                })
            
            # Create request using existing system
            request_data = {
                "patientName": parsed["patientName"],
                "blood": parsed["bloodType"],
                "hospital": parsed["hospital"],
                "latitude": latitude or 0,
                "longitude": longitude or 0,
                "status": "pending",
                "created_by": str(user_id) if user_id else "1",  # Ensure string
                "created_at": firestore.SERVER_TIMESTAMP
            }
            
            doc_ref = db.collection("requests").add(request_data)
            request_id = doc_ref[1].id
            
            # Find eligible donors (with cooldown check)
            from datetime import datetime, timedelta
            all_donors = db.collection("users").where("blood", "==", parsed["bloodType"]).where("status", "==", "approved").stream()
            
            donor_list = []
            notified_count = 0
            
            for donor in all_donors:
                donor_data = donor.to_dict()
                
                # Check cooldown (56 days)
                last_donation = donor_data.get("lastDonationDate")
                if last_donation:
                    if hasattr(last_donation, 'timestamp'):
                        last_donation_dt = datetime.fromtimestamp(last_donation.timestamp())
                        days_since = (datetime.now() - last_donation_dt).days
                        if days_since < 56:
                            continue  # Skip donor in cooldown
                
                donor_list.append(donor_data)
                
                # Send email
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
                    print(f"Email error: {e}")
            
            reply = f"""✅ Request processed successfully!

📋 Extracted Details:
• Blood Type: {parsed['bloodType']}
• Patient: {parsed['patientName']}
• Hospital: {parsed['hospital']}
• Urgency: {parsed['urgency'].upper()}

🎯 Donor Matching:
• Found {len(donor_list)} eligible donors (cooldown checked)
• Notified {notified_count} donors via email
• Request ID: {request_id}

📱 Actions Taken:
✓ Request created in database
✓ {notified_count} donors notified via email
✓ Cooldown period (56 days) checked
✓ Monitoring system activated

⏳ Status: Waiting for donor response..."""
            
            return jsonify({
                "reply": reply,
                "actions": ["extracted", "matched", "notified", "monitoring"],
                "status": "success",
                "request_id": request_id,
                "parsed": parsed
            })
        
        # Donor availability
        elif any(word in msg_lower for word in ["available", "can donate", "ready"]):
            if not user_id:
                return jsonify({"reply": "Please login first to see available requests!", "actions": []})
            
            user_doc = db.collection("users").document(str(user_id)).get()
            if not user_doc.exists:
                return jsonify({"reply": "Please register as a donor first!", "actions": []})
            
            user_data = user_doc.to_dict()
            
            # Check cooldown
            last_donation = user_data.get("lastDonationDate")
            if last_donation:
                from datetime import datetime
                if hasattr(last_donation, 'timestamp'):
                    last_donation_dt = datetime.fromtimestamp(last_donation.timestamp())
                    days_since = (datetime.now() - last_donation_dt).days
                    if days_since < 56:
                        return jsonify({
                            "reply": f"⏳ You're in cooldown period.\n\nYou must wait {56 - days_since} more days before donating again.\n\nLast donation was {days_since} days ago.\nCooldown: 56 days required.",
                            "actions": ["cooldown_check"],
                            "cooldown": True,
                            "days_remaining": 56 - days_since
                        })
            
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
            
            return jsonify({"reply": reply, "actions": ["availability_checked"], "available_requests": len(request_list)})
        
        # Emergency guidance
        elif any(word in msg_lower for word in ["help", "what to do", "first aid", "bleeding"]):
            prompt = f"""User needs emergency guidance: "{message}"
Provide brief first aid advice for blood-related emergencies.
Include: 1. Immediate steps (2-3 points) 2. What NOT to do (1-2 points) 3. When to call ambulance
Keep under 150 words."""
            
            response = groq_client.chat.completions.create(
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

⚠️ This is AI-generated guidance. Always consult medical professionals."""
            
            return jsonify({"reply": reply, "actions": ["guidance_provided"], "type": "emergency_guidance"})
        
        # General query
        else:
            # Check if asking about status
            if any(word in msg_lower for word in ["status", "my request", "check", "update"]):
                if not user_id:
                    return jsonify({"reply": "Please login to check your request status.", "actions": []})
                
                # Get user's latest request - try both string and int user_id
                requests_query1 = db.collection("requests").where("created_by", "==", str(user_id)).stream()
                requests_query2 = db.collection("requests").where("created_by", "==", int(user_id) if str(user_id).isdigit() else user_id).stream()
                
                request_list = []
                for r in requests_query1:
                    request_list.append(dict(r.to_dict(), id=r.id))
                for r in requests_query2:
                    req_dict = dict(r.to_dict(), id=r.id)
                    if req_dict not in request_list:
                        request_list.append(req_dict)
                
                if not request_list:
                    return jsonify({"reply": f"You don't have any requests yet.\n\nYour user ID: {user_id}\n\nTry creating a blood request first!", "actions": []})
                
                # Sort by created_at
                request_list.sort(key=lambda x: x.get('created_at', 0) if x.get('created_at') else 0, reverse=True)
                req = request_list[0]
                
                print(f"Status check - Request: {req}")  # Debug
                
                if req.get('status') == 'completed':
                    reply = f"""✅ Request Completed!

Patient: {req.get('patientName', 'N/A')}
Blood Type: {req.get('blood', 'N/A')}
Status: Donor confirmed and verified

Thank you for using LifeLink! 🙏"""
                elif req.get('status') == 'accepted':
                    donor_name = req.get('donorName', 'A donor')
                    donor_email = req.get('donorEmail', 'N/A')
                    reply = f"""🎉 Great news!

{donor_name} has accepted your request for {req.get('blood', 'N/A')} blood!

Patient: {req.get('patientName', 'N/A')}
Hospital: {req.get('hospital', 'N/A')}
Donor: {donor_name}
Email: {donor_email}

Status: ✅ ACCEPTED - Awaiting admin verification
The donor will be contacted shortly!"""
                else:
                    reply = f"""⏳ Request In Progress

Patient: {req.get('patientName', 'N/A')}
Blood Type: {req.get('blood', 'N/A')}
Hospital: {req.get('hospital', 'N/A')}
Status: {req.get('status', 'pending').upper()}

📊 Current Status: Searching for donors
I'm continuously monitoring. You'll be notified when someone accepts!

Request ID: {req.get('id', 'N/A')}"""
                
                return jsonify({"reply": reply, "actions": ["status_checked"], "request": req})
            
            # General query
            prompt = f"""User query: "{message}"
You are LifeLink AI, an emergency blood donation assistant.
Provide helpful, concise response about: system, blood donation, eligibility, how to help.
Keep under 100 words. Be friendly."""
            
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            return jsonify({"reply": response.choices[0].message.content.strip(), "actions": ["general_response"], "type": "general"})
            
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"reply": f"Sorry, I encountered an error: {str(e)}", "actions": [], "status": "error"})



if __name__ == "__main__":
    print("="*60)
    print("🤖 LifeLink Backend Starting...")
    print("✓ All Features: Login, Register, Cooldown, Email")
    print("✓ Agentic Chatbot: Natural language blood requests")
    print("✓ Firebase: Cloud database")
    print("="*60)
    print("🚀 Server running on http://localhost:5000")
    print("📱 Open http://localhost:3000/dashboard.html")
    print("="*60)
    app.run(debug=True, port=5000, use_reloader=False, host='0.0.0.0')
