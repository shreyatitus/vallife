import os
import json
from anthropic import Anthropic
from database import get_db

class CommunicationAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    def generate_donor_message(self, donor, request_info, urgency="medium"):
        """Generate personalized message for donor using LLM"""
        prompt = f"""Generate a personalized, empathetic message to request blood donation.

Donor Info:
- Name: {donor['name']}
- Past Donations: {donor['donations']}
- Points: {donor['points']}

Request Info:
- Patient: {request_info.get('patientName', 'A patient')}
- Hospital: {request_info.get('hospital', 'Local hospital')}
- Distance: {donor.get('distance', 'nearby')} km
- Urgency: {urgency}

Create a message that:
1. Addresses donor by name
2. Acknowledges their contribution history
3. Explains the urgency appropriately
4. Provides clear next steps
5. Is concise (under 150 words)

Return only the message text, no JSON."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text.strip()
    
    def send_notification(self, donor_id, request_id, message_text):
        """Send notification and log it"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (donor_id, request_id, message, status)
            VALUES (%s, %s, %s, 'sent')
        """, (donor_id, request_id, message_text))
        conn.commit()
        notification_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return notification_id
    
    def handle_donor_response(self, notification_id, response, response_time):
        """Process donor response and update patterns"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Update notification status
        cursor.execute("""
            UPDATE notifications 
            SET status=%s, response_time=%s 
            WHERE id=%s
        """, (response, response_time, notification_id))
        
        # Get donor and request info
        cursor.execute("""
            SELECT donor_id, request_id FROM notifications WHERE id=%s
        """, (notification_id,))
        notif = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return notif
    
    def generate_followup_message(self, donor, previous_message, reason="no_response"):
        """Generate intelligent follow-up message"""
        prompt = f"""Generate a follow-up message for a blood donor who hasn't responded.

Previous Message: {previous_message}
Donor Name: {donor['name']}
Reason: {reason}

Create a brief, respectful follow-up that:
1. Doesn't pressure the donor
2. Provides alternative options
3. Reiterates urgency if critical
4. Under 100 words

Return only the message text."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=384,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text.strip()
