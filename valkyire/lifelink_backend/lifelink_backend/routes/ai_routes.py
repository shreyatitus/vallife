from flask import Blueprint, request, jsonify
from services.ai_agent_service import chat

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    message = data.get('message')
    history = data.get('history', [])
    
    if not message:
        return jsonify({'error': 'Message required'}), 400
    
    response = chat(message, history)
    return jsonify({'response': response})
