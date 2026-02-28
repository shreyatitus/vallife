from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "LifeLink API Running", "version": "1.0"})

@app.route("/ai-chat", methods=["POST"])
def ai_chat():
    data = request.json
    user_message = data.get("message", "")
    conversation_history = data.get("history", [])
    
    try:
        from services.groq_assistant import chat_with_assistant
        response = chat_with_assistant(user_message, conversation_history)
        return jsonify({"response": response})
    except Exception as e:
        print(f"AI Chat Error: {str(e)}")
        return jsonify({"response": f"Error: {str(e)}"})

if __name__ == "__main__":
    print("LifeLink AI Chat Server Starting...")
    print("Server running on http://localhost:5000")
    app.run(debug=True, port=5000)
