from datetime import datetime, timedelta
from database import get_db
import json

class MonitorAgent:
    def __init__(self):
        self.check_interval = 300  # 5 minutes
        
    def monitor_pending_requests(self):
        """Monitor all pending requests and trigger actions"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Find requests with no response after 15 minutes
        cursor.execute("""
            SELECT r.*, 
                   (SELECT COUNT(*) FROM notifications n 
                    WHERE n.request_id = r.id AND n.status = 'accepted') as accepted_count,
                   (SELECT COUNT(*) FROM notifications n 
                    WHERE n.request_id = r.id) as total_notifications
            FROM requests r
            WHERE r.status = 'pending' 
            AND r.created_at < DATE_SUB(NOW(), INTERVAL 15 MINUTE)
        """)
        
        stalled_requests = cursor.fetchall()
        cursor.close()
        conn.close()
        
        actions = []
        for req in stalled_requests:
            if req['accepted_count'] == 0:
                if req['total_notifications'] < 3:
                    actions.append({
                        'request_id': req['id'],
                        'action': 'expand_search',
                        'reason': 'No responses received'
                    })
                else:
                    actions.append({
                        'request_id': req['id'],
                        'action': 'escalate',
                        'reason': 'Multiple attempts failed'
                    })
        
        return actions
    
    def calculate_success_metrics(self):
        """Calculate system performance metrics"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Success rate
        cursor.execute("""
            SELECT 
                COUNT(*) as total_requests,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                AVG(TIMESTAMPDIFF(MINUTE, created_at, 
                    (SELECT created_at FROM notifications 
                     WHERE request_id = requests.id AND status = 'accepted' 
                     LIMIT 1))) as avg_match_time
            FROM requests
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        
        metrics = cursor.fetchone()
        
        # Donor response rates
        cursor.execute("""
            SELECT 
                AVG(response_time) as avg_response_time,
                SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) / COUNT(*) as acceptance_rate
            FROM notifications
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        
        donor_metrics = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            'success_rate': metrics['completed'] / metrics['total_requests'] if metrics['total_requests'] > 0 else 0,
            'avg_match_time_minutes': metrics['avg_match_time'] or 0,
            'donor_acceptance_rate': donor_metrics['acceptance_rate'] or 0,
            'avg_donor_response_time': donor_metrics['avg_response_time'] or 0
        }
    
    def log_agent_decision(self, request_id, agent_type, decision, reasoning, confidence):
        """Log agent decisions for analysis and improvement"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO agent_decisions (request_id, agent_type, decision, reasoning, confidence)
            VALUES (%s, %s, %s, %s, %s)
        """, (request_id, agent_type, json.dumps(decision), reasoning, confidence))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def get_optimization_insights(self):
        """Analyze agent decisions to provide optimization insights"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT agent_type, AVG(confidence) as avg_confidence, COUNT(*) as decision_count
            FROM agent_decisions
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY agent_type
        """)
        
        insights = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return insights
