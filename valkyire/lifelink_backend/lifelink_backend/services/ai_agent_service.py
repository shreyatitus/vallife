import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def chat(message, conversation_history=[]):
    system_prompt = """You are a helpful blood donation assistant for LifeLink. 
    Help users with: eligibility criteria, donation process, health requirements, 
    finding donors, and general blood donation questions. Be concise and supportive."""
    
    messages = conversation_history + [{"role": "user", "content": message}]
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        system=system_prompt,
        messages=messages
    )
    
    return response.content[0].text
