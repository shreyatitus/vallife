from datetime import datetime, timedelta
from database import get_db
import threading
import time

class AutoEscalationService:
    """Autonomous service that monitors and escalates requests"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.running = False
        self.check_interval = 300  # 5 minutes
    
    def start_monitoring(self):
        """Start autonomous monitoring in background"""
        self.running = True
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()
        print("🤖 Auto-escalation service started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
    
    def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.running:
            try:
                self._check_and_escalate()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(60)
    
    def _check_and_escalate(self):
        """Check pending requests and take action"""
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Find requests needing action
        cursor.execute("""
            SELECT r.*, 
                   (SELECT COUNT(*) FROM notifications n 
                    WHERE n.request_id = r.id) as notification_count,
                   (SELECT MAX(n.created_at) FROM notifications n 
                    WHERE n.request_id = r.id) as last_notification,
                   TIMESTAMPDIFF(MINUTE, r.created_at, NOW()) as minutes_elapsed
            FROM requests r
            WHERE r.status = 'pending'
        """)
        
        requests = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for req in requests:
            minutes = req['minutes_elapsed']
            notif_count = req['notification_count']
            
            # Escalation logic based on time and attempts
            if minutes >= 10 and notif_count == 1:
                # After 10 min, contact backup donor
                self._expand_search(req['id'], "10 minutes elapsed")
            
            elif minutes >= 20 and notif_count == 2:
                # After 20 min, contact more donors
                self._expand_search(req['id'], "20 minutes elapsed")
            
            elif minutes >= 30 and notif_count >= 3:
                # After 30 min, escalate to blood banks
                self._escalate_to_blood_banks(req['id'])
    
    def _expand_search(self, request_id, reason):
        """Expand search and contact more donors"""
        print(f"🔄 Auto-expanding search for request {request_id}: {reason}")
        
        result = self.orchestrator.autonomous_retry(request_id)
        
        # Log action
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO escalation_log (request_id, action, reason, result)
            VALUES (%s, 'expand_search', %s, %s)
        """, (request_id, reason, str(result)))
        conn.commit()
        cursor.close()
        conn.close()
        
        return result
    
    def _escalate_to_blood_banks(self, request_id):
        """Escalate to blood banks and emergency services"""
        print(f"🚨 Escalating request {request_id} to blood banks")
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Get request details
        cursor.execute("SELECT * FROM requests WHERE id=%s", (request_id,))
        request = cursor.fetchone()
        
        # Mark as escalated
        cursor.execute("""
            UPDATE requests 
            SET status='escalated', escalated_at=NOW() 
            WHERE id=%s
        """, (request_id,))
        
        # Log escalation
        cursor.execute("""
            INSERT INTO escalation_log (request_id, action, reason, result)
            VALUES (%s, 'escalate_blood_bank', 'Multiple donor attempts failed', 'Escalated')
        """, (request_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # In production: Send to blood bank API, emergency services, etc.
        return {
            "status": "escalated",
            "request_id": request_id,
            "blood_type": request['blood'],
            "hospital": request['hospital']
        }
    
    def get_escalation_stats(self):
        """Get escalation statistics"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                action,
                COUNT(*) as count,
                DATE(created_at) as date
            FROM escalation_log
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY action, DATE(created_at)
            ORDER BY date DESC
        """)
        
        stats = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return stats
