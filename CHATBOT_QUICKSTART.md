# 🚀 Quick Start - Agentic Chatbot

## 3-Minute Setup

### Step 1: Set API Key
```bash
# Windows Command Prompt
set ANTHROPIC_API_KEY=your_key_here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="your_key_here"

# Linux/Mac
export ANTHROPIC_API_KEY=your_key_here
```

Get your key: https://console.anthropic.com/

### Step 2: Update Database
```bash
cd valkyire\lifelink_backend\lifelink_backend
python add_escalation_table.py
```

### Step 3: Start Backend
```bash
python app.py
```

Wait for:
```
🤖 LifeLink Agentic AI System Starting...
✓ Chatbot Agent: Conversational interface with autonomous actions
✓ Auto-Escalation: Background monitoring every 5 minutes
🚀 System ready! Chatbot endpoint: POST /chat
```

### Step 4: Test It!

**Option A: Open Web Interface**
- Open `chatbot.html` in your browser
- Start chatting!

**Option B: Run Demo**
```bash
python demo_agentic_chatbot.py
```

**Option C: Test with curl**
```bash
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d "{\"user_id\":1,\"message\":\"Need O+ blood urgently\"}"
```

---

## 💬 Try These Messages

1. **Blood Request:**
   - "Need O+ blood urgently at City Hospital"
   - "Emergency! Accident victim needs A- blood"

2. **Donor Availability:**
   - "I am available to donate"
   - "Can donate blood today"

3. **Status Check:**
   - "Check my request status"
   - "What's the status of my request?"

4. **Emergency Help:**
   - "What to do for heavy bleeding?"
   - "First aid for blood loss"

5. **General:**
   - "How does LifeLink work?"
   - "Am I eligible to donate?"

---

## 🎯 What You'll See

The AI will:
1. ✅ Extract details from your message
2. ✅ Find matching donors automatically
3. ✅ Notify donors via SMS
4. ✅ Monitor responses continuously
5. ✅ Auto-retry if no response
6. ✅ Escalate after 30 minutes

**This is TRUE agentic behavior!**

---

## 🐛 Troubleshooting

**Backend won't start?**
- Check if port 5000 is free
- Verify ANTHROPIC_API_KEY is set
- Run: `pip install -r requirements.txt`

**Chatbot not responding?**
- Check backend is running
- Open browser console (F12)
- Verify API_URL in chatbot.html

**Database errors?**
- Run: `python database.py`
- Then: `python add_escalation_table.py`

---

## 📊 Monitor the System

**Check escalation stats:**
```bash
curl http://localhost:5000/escalation-stats
```

**View system insights:**
```bash
curl http://localhost:5000/system-insights
```

**Trigger manual monitoring:**
```bash
curl -X POST http://localhost:5000/autonomous-monitor
```

---

## 🎬 For Demo/Pitch

1. Open `chatbot.html` in browser
2. Type: "URGENT! Need O+ blood at City Hospital"
3. Show the AI response with extracted details
4. Highlight the autonomous actions taken
5. Explain the background monitoring
6. Show escalation timeline

**Key Points to Emphasize:**
- "The AI doesn't just chat - it ACTS"
- "Autonomous monitoring every 5 minutes"
- "Auto-escalates after 30 minutes"
- "Learns from donor patterns"
- "Zero manual intervention needed"

---

## 🏆 Success!

You now have a fully functional agentic AI chatbot that:
- Understands natural language
- Takes autonomous actions
- Monitors continuously
- Escalates intelligently
- Learns and adapts

**Perfect for the hackathon! 🚀**
