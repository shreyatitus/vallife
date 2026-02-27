import { API_BASE_URL } from './config.js';

let history = [];

async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessageToChat('You', message);
    input.value = '';
    
    try {
        const response = await fetch(`${API_BASE_URL}/ai/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, history })
        });
        
        const data = await response.json();
        addMessageToChat('Assistant', data.response);
        
        history.push({ role: 'user', content: message });
        history.push({ role: 'assistant', content: data.response });
    } catch (error) {
        addMessageToChat('Error', 'Failed to get response');
    }
}

function addMessageToChat(sender, text) {
    const chatBox = document.getElementById('chat-box');
    const msg = document.createElement('div');
    msg.style.marginBottom = '10px';
    msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById('message-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

window.sendMessage = sendMessage;
