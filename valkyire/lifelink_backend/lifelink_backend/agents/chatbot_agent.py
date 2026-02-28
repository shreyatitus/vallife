import os
import json
from anthropic import Anthropic
try:
    from firebase_admin import firestore
    FIREBASE_MODE = True
except:
    FIREBASE_MODE = False
    from database import get_db

class ChatbotAgent:
    """Conversational agent that handles user interactions and coordinates actions"""
    
    def __init__(self, orchestrator):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.orchestrator = orchestrator
        self.conversation_history = {}
    
    def process_message(self, user_id, message, latitude=None, longitude=None):
        """Process user message and take autonomous actions"""
        
        # Detect intent
        intent = self._detect_intent(message)
        
        if intent == "blood_request":
            return self._handle_blood_request(user_id, message, latitude, longitude)
        elif intent == "donor_availability":
            return self._handle_donor_availability(user_id, message)
        elif intent == "emergency_guidance":
            return self._handle_emergency_guidance(message)
        elif intent == "status_check":
            return self._handle_status_check(user_id)
        else:
            return self._handle_general_query(message)
    
    def _detect_intent(self, message):
        """Detect user intent from message"""
        msg_lower = message.lower()
        
        blood_keywords = ["need", "urgent", "blood", "emergency", "accident", "patient"]
        availability_keywords = ["available", "can donate", "ready to donate"]
        guidance_keywords = ["help", "what to do", "first aid", "how to"]
        status_keywords = ["status", "my request", "pending", "waiting"]
        
        if any(k in msg_lower for k in blood_keywords):
            return "blood_request"
        elif any(k in msg_lower for k in availability_keywords):
            return "donor_availability"
        elif any(k in msg_lower for k in guidance_keywords):
            return "emergency_guidance"
        elif any(k in msg_lower for k in status_keywords):
            return "status_check"
        return "general"
    
    def _handle_blood_request(self, user_id, message, latitude, longitude):
        """Handle blood request with full autonomous workflow"""
        
        # Step 1: Parse request
        parsed = self.orchestrator.coordinator.nlp_agent.parse_natural_language_request(message)
        
        if not parsed.get("bloodType"):
            return {
                "reply": "I couldn't determine the blood type. Please specify (e.g., 'Need O+ blood urgently')",
                "actions": [],
                "status": "clarification_needed"
            }
        
        # Step 2: Create request in database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO requests (patientName, blood, hospital, latitude, longitude, 
                                urgency, natural_language_request, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            parsed["patientName"], parsed["bloodType"], parsed["hospital"],
            latitude or 0, longitude or 0, parsed["urgency"], message, user_id
        ))
        conn.commit()
        request_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        # Step 3: Process with orchestrator
        result = self.orchestrator.process_blood_request(request_id, {
            "patientName": parsed["patientName"],
            "blood": parsed["bloodType"],
            "hospital": parsed["hospital"],
            "latitude": latitude or 0,
            "longitude": longitude or 0
        })
        
        # Step 4: Generate conversational response
        if result["status"] == "success":
            donor = result["primary_donor"]
            reply = f"""✅ Request processed successfully!

📋 Extracted Details:
• Blood Type: {parsed['bloodType']}
• Patient: {parsed['patientName']}
• Hospital: {parsed['hospital']}
• Urgency: {parsed['urgency'].upper()}

🎯 Donor Matching:
• Found {result['backup_count'] + 1} eligible donors
• Top match: {donor['name']} ({donor['distance']:.1f} km away)
• Availability score: {donor['availability_score']:.0%}

📱 Actions Taken:
✓ Notified {donor['name']} via SMS
✓ {result['backup_count']} backup donors on standby
✓ Monitoring system activated

⏳ Status: Waiting for donor response...
I'll notify you immediately when someone accepts!"""
            
            actions = ["extracted", "matched", "notified", "monitoring"]
        else:
            reply = f"""⚠️ Request received but no donors found immediately.

📋 Details:
• Blood Type: {parsed['bloodType']}
• Urgency: {parsed['urgency'].upper()}

🔄 Actions:
• Expanding search radius
• Checking nearby blood banks
• Will notify you when donors become available"""
            
            actions = ["extracted", "searching"]
        
        return {
            "reply": reply,
            "actions": actions,
            "status": result["status"],
            "request_id": request_id,
            "parsed": parsed
        }
    
    def _handle_donor_availability(self, user_id, message):
        """Handle donor saying they're available"""
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Get user's blood type
        cursor.execute("SELECT blood, name FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return {
                "reply": "Please register as a donor first to help save lives!",
                "actions": []
            }
        
        # Find pending requests matching blood type
        cursor.execute("""
            SELECT * FROM requests 
            WHERE blood=%s AND status='pending' 
            ORDER BY created_at DESC LIMIT 3
        """, (user['blood'],))
        requests = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if requests:
            req_list = "\n".join([
                f"• {r['patientName']} at {r['hospital']} ({r['urgency']} urgency)"
                for r in requests
            ])
            
            reply = f"""🙏 Thank you, {user['name']}!

Active requests for {user['blood']} blood:
{req_list}

You can accept any request from the dashboard.
Your willingness to help is truly appreciated! ❤️"""
        else:
            reply = f"""Thank you for your willingness to donate, {user['name']}! 

Currently no active requests for {user['blood']} blood.
We'll notify you immediately when someone needs your help. 🙏"""
        
        return {
            "reply": reply,
            "actions": ["availability_updated"],
            "available_requests": len(requests)
        }
    
    def _handle_emergency_guidance(self, message):
        """Provide emergency first aid guidance"""
        
        prompt = f"""User needs emergency guidance: "{message}"

Provide brief, actionable first aid advice for blood-related emergencies.
Include:
1. Immediate steps (2-3 points)
2. What NOT to do (1-2 points)
3. When to call ambulance

Keep under 150 words. Be clear and calm."""
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        
        guidance = response.content[0].text.strip()
        
        reply = f"""🚑 Emergency Guidance:

{guidance}

📞 Emergency Numbers:
• Ambulance: 108
• Blood Bank Helpline: 104

⚠️ This is AI-generated guidance. Always consult medical professionals for emergencies."""
        
        return {
            "reply": reply,
            "actions": ["guidance_provided"],
            "type": "emergency_guidance"
        }
    
    def _handle_status_check(self, user_id):
        """Check status of user's requests"""
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT r.*, 
                   (SELECT COUNT(*) FROM notifications n 
                    WHERE n.request_id = r.id) as notifications_sent,
                   (SELECT COUNT(*) FROM notifications n 
                    WHERE n.request_id = r.id AND n.status = 'accepted') as accepted_count
            FROM requests r
            WHERE r.created_by=%s
            ORDER BY r.created_at DESC LIMIT 1
        """, (user_id,))
        
        request = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not request:
            return {
                "reply": "You don't have any active requests.",
                "actions": []
            }
        
        if request['status'] == 'completed':
            reply = f"""✅ Request Completed!

Patient: {request['patientName']}
Blood Type: {request['blood']}
Status: Donor confirmed and verified

Thank you for using LifeLink! 🙏"""
        elif request['accepted_count'] > 0:
            reply = f"""🎉 Great news!

A donor has accepted your request for {request['blood']} blood!
Patient: {request['patientName']}
Hospital: {request['hospital']}

Status: Awaiting admin verification"""
        else:
            reply = f"""⏳ Request In Progress

Patient: {request['patientName']}
Blood Type: {request['blood']}
Hospital: {request['hospital']}
Urgency: {request.get('urgency', 'medium').upper()}

📊 Status:
• {request['notifications_sent']} donors contacted
• Monitoring system active
• Auto-retry enabled

I'm continuously searching for donors. You'll be notified immediately when someone accepts!"""
        
        return {
            "reply": reply,
            "actions": ["status_checked"],
            "request": request
        }
    
    def _handle_general_query(self, message):
        """Handle general queries about the system"""
        
        prompt = f"""User query: "{message}"

You are LifeLink AI, an emergency blood donation assistant.
Provide a helpful, concise response about:
- How the system works
- Blood donation process
- Eligibility criteria
- How to help

Keep under 100 words. Be friendly and encouraging."""
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=384,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "reply": response.content[0].text.strip(),
            "actions": ["general_response"],
            "type": "general"
        }
