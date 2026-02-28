from groq import Groq
import json

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def chat_with_assistant(user_message, conversation_history=[], db=None):
    system_prompt = """You are an AI assistant for LifeLink blood donation platform. Your job is to help users create blood requests through conversation.

When a user needs blood, collect these details step by step:
1. Patient name
2. Blood type needed (A+, A-, B+, B-, O+, O-, AB+, AB-)
3. Hospital name
4. Location (city/area name as text)

Ask ONE question at a time. Be conversational and friendly.

Once you have ALL details, respond with EXACTLY this format:
BLOOD_REQUEST_COMPLETE:
{
  "patientName": "name",
  "blood": "blood_type",
  "hospital": "hospital_name",
  "location": "city_or_area_name",
  "latitude": 0,
  "longitude": 0
}

If user asks general questions, answer them normally."""
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        return f"I'm experiencing technical difficulties. Error: {str(e)}"

def process_blood_request_workflow(db, request_data):
    """Process complete blood request workflow"""
    from services.ai_donor_matcher import process_blood_request_ai
    
    # Create request in database
    request_ref = db.collection("requests").add(request_data)
    request_id = request_ref[1].id
    
    # AI matches and notifies donors
    result = process_blood_request_ai(db, request_id, request_data)
    
    return result
