import os
import json
from anthropic import Anthropic

class NLPAgent:
    """Agent for processing natural language blood requests"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    def parse_natural_language_request(self, text):
        """Parse natural language request into structured data"""
        prompt = f"""Parse this blood donation request into structured data.

Request: "{text}"

Extract and return JSON with:
- patientName: string
- bloodType: string (A+, A-, B+, B-, AB+, AB-, O+, O-)
- hospital: string
- urgency: string (critical/high/medium/low)
- additionalInfo: string

If information is missing, use null. Infer urgency from language used."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            return json.loads(message.content[0].text)
        except:
            return {
                "patientName": "Unknown",
                "bloodType": None,
                "hospital": "Unknown",
                "urgency": "medium",
                "additionalInfo": text
            }
    
    def extract_location_from_text(self, text):
        """Extract location information from text"""
        prompt = f"""Extract location information from this text.

Text: "{text}"

Return JSON with:
- city: string
- hospital: string
- address: string (if mentioned)
- needsGeocoding: boolean (true if we need to convert to coordinates)

If no location found, return null values."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=384,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            return json.loads(message.content[0].text)
        except:
            return {
                "city": None,
                "hospital": None,
                "address": None,
                "needsGeocoding": True
            }
