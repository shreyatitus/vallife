from agents.coordinator_agent import CoordinatorAgent
from agents.matcher_agent import MatcherAgent
from agents.communication_agent import CommunicationAgent
from agents.monitor_agent import MonitorAgent
from agents.nlp_agent import NLPAgent
from database import get_db
import json

class AgentOrchestrator:
    """Main orchestrator that coordinates all agents autonomously"""
    
    def __init__(self):
        self.coordinator = CoordinatorAgent()
        self.matcher = MatcherAgent()
        self.communicator = CommunicationAgent()
        self.monitor = MonitorAgent()
        self.nlp_agent = NLPAgent()
    
    def process_blood_request(self, request_id, request_data):
        """Autonomous multi-agent workflow for blood requests"""
        
        # Step 1: Coordinator analyzes request
        analysis = self.coordinator.analyze_request(request_data)
        urgency = analysis.get('urgency', 'medium')
        
        # Log analysis
        self.monitor.log_agent_decision(
            request_id, 'coordinator', analysis, 
            analysis.get('reasoning', ''), 0.85
        )
        
        # Update request with analysis
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE requests 
            SET urgency=%s, agent_analysis=%s 
            WHERE id=%s
        """, (urgency, json.dumps(analysis), request_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Step 2: Matcher finds optimal donors
        donors = self.matcher.find_optimal_donors(
            request_data['blood'],
            request_data.get('latitude', 0),
            request_data.get('longitude', 0),
            urgency
        )
        
        if not donors:
            return {
                'status': 'failed',
                'message': 'No eligible donors found',
                'analysis': analysis
            }
        
        # Step 3: Coordinator makes strategic decision
        decision = self.coordinator.make_decision(request_id, analysis, donors[:5])
        
        self.monitor.log_agent_decision(
            request_id, 'coordinator_decision', decision,
            'Strategic donor selection', 0.9
        )
        
        # Step 4: Communication agent contacts donors
        primary_donor = decision.get('primary_donor') or donors[0]
        
        message = self.communicator.generate_donor_message(
            primary_donor, request_data, urgency
        )
        
        notification_id = self.communicator.send_notification(
            primary_donor['id'], request_id, message
        )
        
        # Step 5: Schedule backup contacts
        backup_donors = decision.get('backup_donors', donors[1:3])
        
        return {
            'status': 'success',
            'primary_donor': {
                'name': primary_donor['name'],
                'phone': primary_donor['phone'],
                'distance': primary_donor['distance'],
                'availability_score': primary_donor.get('availability_score', 0.5)
            },
            'backup_count': len(backup_donors),
            'urgency': urgency,
            'analysis': analysis,
            'message_sent': message,
            'notification_id': notification_id
        }
    
    def autonomous_retry(self, request_id):
        """Autonomous retry logic when donor doesn't respond"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Get request details
        cursor.execute("SELECT * FROM requests WHERE id=%s", (request_id,))
        request = cursor.fetchone()
        
        # Get previous notifications
        cursor.execute("""
            SELECT * FROM notifications 
            WHERE request_id=%s 
            ORDER BY created_at DESC
        """, (request_id,))
        notifications = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        contacted_donor_ids = [n['donor_id'] for n in notifications]
        
        # Find new donors excluding already contacted
        donors = self.matcher.find_optimal_donors(
            request['blood'],
            float(request['latitude']),
            float(request['longitude']),
            request.get('urgency', 'medium')
        )
        
        new_donors = [d for d in donors if d['id'] not in contacted_donor_ids]
        
        if new_donors:
            next_donor = new_donors[0]
            message = self.communicator.generate_donor_message(
                next_donor, request, request.get('urgency', 'medium')
            )
            
            self.communicator.send_notification(
                next_donor['id'], request_id, message
            )
            
            return {
                'status': 'retry_sent',
                'donor': next_donor['name'],
                'attempt': len(notifications) + 1
            }
        
        return {
            'status': 'exhausted',
            'message': 'All available donors contacted'
        }
    
    def run_autonomous_monitoring(self):
        """Continuously monitor and take autonomous actions"""
        actions = self.monitor.monitor_pending_requests()
        
        results = []
        for action in actions:
            if action['action'] == 'expand_search':
                result = self.autonomous_retry(action['request_id'])
                results.append(result)
            elif action['action'] == 'escalate':
                # Escalate to blood banks or emergency services
                results.append({
                    'status': 'escalated',
                    'request_id': action['request_id']
                })
        
        return results
    
    def get_system_insights(self):
        """Get AI-driven insights about system performance"""
        metrics = self.monitor.calculate_success_metrics()
        insights = self.monitor.get_optimization_insights()
        
        return {
            'metrics': metrics,
            'agent_performance': insights
        }
