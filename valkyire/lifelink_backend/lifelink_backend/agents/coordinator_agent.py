import os
import json
from anthropic import Anthropic
from agents.nlp_agent import NLPAgent

class CoordinatorAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.nlp_agent = NLPAgent()
        
    def analyze_request(self, request_data):
        """Analyze blood request using LLM to determine urgency and context"""
        prompt = f"""Analyze this blood donation request and provide:
1. Urgency level (critical/high/medium/low)
2. Key context factors
3. Recommended action plan

Request: {json.dumps(request_data)}

Respond in JSON format with: urgency, context, action_plan, reasoning"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            response = json.loads(message.content[0].text)
            return response
        except:
            return {
                "urgency": "medium",
                "context": "Standard request",
                "action_plan": "Find nearest eligible donor",
                "reasoning": "Default analysis"
            }
    
    def make_decision(self, request_id, analysis, donor_options):
        """Make intelligent decision on donor selection"""
        prompt = f"""You are a blood donation coordinator AI. Given this analysis and donor options, decide the best strategy.

Analysis: {json.dumps(analysis)}
Available Donors: {json.dumps(donor_options)}

Provide:
1. Primary donor selection with reasoning
2. Backup donors (ranked)
3. Communication strategy
4. Contingency plan if primary declines

Respond in JSON format."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            return json.loads(message.content[0].text)
        except:
            return {
                "primary_donor": donor_options[0] if donor_options else None,
                "backup_donors": donor_options[1:3] if len(donor_options) > 1 else [],
                "strategy": "Contact in order of proximity",
                "contingency": "Expand search radius"
            }
