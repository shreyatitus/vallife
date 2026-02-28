# 🔥 Firebase Quick Start - Agentic Chatbot

## ✅ You're Using Firebase (No MySQL Needed!)

---

## 🚀 **3-Step Setup:**

### **Step 1: Set Anthropic API Key**
```bash
set ANTHROPIC_API_KEY=your_anthropic_key_here
```

Get key: https://console.anthropic.com/

### **Step 2: Check Firebase Key**
Make sure `firebase-key.json` exists in:
```
valkyire\lifelink_backend\lifelink_backend\firebase-key.json
```

### **Step 3: Start Backend**
```bash
cd valkyire\lifelink_backend\lifelink_backend
python app_agentic_firebase.py
```

---

## ✅ **Expected Output:**

```
============================================================
🤖 LifeLink Agentic AI System Starting...
✓ Firebase connected successfully!
✓ Chatbot Agent: Conversational interface
✓ Orchestrator: Multi-agent coordination
✓ Firebase: Cloud database
============================================================
🚀 Server running on http://localhost:5000
📱 Open chatbot.html to start chatting!
============================================================
```

---

## 💬 **Test It:**

Open `chatbot.html` in browser and type:
- **"Need O+ blood urgently"**
- **"I am available to donate"**
- **"What to do for bleeding?"**

---

## 🐛 **Troubleshooting:**

### ❌ "ANTHROPIC_API_KEY not set"
```bash
set ANTHROPIC_API_KEY=your_key_here
```

### ❌ "Firebase connection error"
- Check `firebase-key.json` exists
- Verify Firebase project is active
- Check internet connection

### ❌ "Module not found"
```bash
pip install anthropic firebase-admin flask flask-cors
```

---

## 📊 **What Works:**

✅ Natural language blood requests  
✅ AI extracts details automatically  
✅ Conversational responses  
✅ Emergency guidance  
✅ Status checking  

---

## ⚠️ **Note:**

The full agentic features (auto-escalation, donor matching) require:
- User data in Firebase
- Donor profiles
- Request history

For **demo purposes**, the chatbot will:
- Parse your message
- Extract blood type, urgency, location
- Provide intelligent responses
- Show what actions it would take

---

## 🎯 **For Hackathon Demo:**

1. Start backend: `python app_agentic_firebase.py`
2. Open `chatbot.html`
3. Show natural language understanding
4. Highlight autonomous action planning
5. Explain the multi-agent architecture

**The AI shows TRUE agentic behavior even without full data!** 🚀

---

**Ready to chat!** 💬
