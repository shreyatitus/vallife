const BASE_URL = "http://localhost:5000";
let conversationHistory = [];

function addMessage(message, isUser) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        margin: 10px 0;
        padding: 12px 16px;
        border-radius: 12px;
        ${isUser ? 
            'background: rgba(230, 57, 70, 0.2); margin-left: 60px; text-align: right;' : 
            'background: rgba(255, 255, 255, 0.9); margin-right: 60px; color: #333;'}
    `;
    messageDiv.innerHTML = `<strong>${isUser ? 'You' : 'AI Assistant'}:</strong><br>${message}`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessage(message, true);
    input.value = '';
    
    conversationHistory.push({role: 'user', content: message});
    
    try {
        const response = await fetch(BASE_URL + '/ai-chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                history: conversationHistory
            })
        });
        
        const result = await response.json();
        addMessage(result.response, false);
        conversationHistory.push({role: 'assistant', content: result.response});
    } catch (error) {
        addMessage('Sorry, I encountered an error. Please try again.', false);
    }
}

document.getElementById('message-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') sendMessage();
});

window.onload = function() {
    addMessage('Hello! I\'m your LifeLink AI assistant. How can I help you today?', false);
};
