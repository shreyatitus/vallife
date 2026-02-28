# ✅ Testing Checklist - Verify All Features Work

## Pre-Testing Setup

- [ ] ANTHROPIC_API_KEY is set
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`python database.py`)
- [ ] Escalation table added (`python add_escalation_table.py`)
- [ ] Backend running (`python app.py`)

---

## 1️⃣ Test Chatbot Endpoint

### Test Natural Language Blood Request

```bash
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d "{\"user_id\":1,\"message\":\"Need O+ blood urgently at City Hospital\",\"latitude\":10.5276,\"longitude\":76.2144}"
```

**Expected Response:**
- [ ] Status 200
- [ ] `reply` field with extracted details
- [ ] `actions` array with ["extracted", "matched", "notified", "monitoring"]
- [ ] `status` = "success"
- [ ] `request_id` present

### Test Donor Availability

```bash
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d "{\"user_id\":1,\"message\":\"I am available to donate\"}"
```

**Expected Response:**
- [ ] Status 200
- [ ] Thank you message
- [ ] List of matching requests (if any)
- [ ] `actions` = ["availability_updated"]

### Test Emergency Guidance

```bash
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d "{\"user_id\":1,\"message\":\"What to do for heavy bleeding?\"}"
```

**Expected Response:**
- [ ] Status 200
- [ ] First aid guidance
- [ ] Emergency numbers
- [ ] Safety disclaimer
- [ ] `actions` = ["guidance_provided"]

### Test Status Check

```bash
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d "{\"user_id\":1,\"message\":\"Check my request status\"}"
```

**Expected Response:**
- [ ] Status 200
- [ ] Request details or "no active requests"
- [ ] `actions` = ["status_checked"]

---

## 2️⃣ Test Auto-Escalation Service

### Check Service is Running

**Look for in console output:**
```
🤖 Auto-escalation service started
```

- [ ] Message appears on backend startup

### Test Autonomous Monitoring

```bash
curl -X POST http://localhost:5000/autonomous-monitor
```

**Expected Response:**
- [ ] Status 200
- [ ] `actions_taken` array (may be empty if no pending requests)

### Test Escalation Stats

```bash
curl http://localhost:5000/escalation-stats
```

**Expected Response:**
- [ ] Status 200
- [ ] `stats` array with escalation history

---

## 3️⃣ Test Web Interface

### Open chatbot.html

- [ ] Page loads without errors
- [ ] Chat interface displays
- [ ] Welcome message appears
- [ ] Quick action buttons visible
- [ ] Input field functional

### Test Conversations

**Type:** "Need O+ blood urgently"

- [ ] Message appears on right (user)
- [ ] Typing indicator shows
- [ ] AI response appears on left (bot)
- [ ] Action badges display
- [ ] Response includes extracted details

**Type:** "I am available to donate"

- [ ] AI responds with thank you
- [ ] Shows matching requests (if any)

**Type:** "What to do for bleeding?"

- [ ] AI provides first aid guidance
- [ ] Emergency numbers included

### Test Quick Actions

- [ ] Click "🩸 Need Blood" - sends message
- [ ] Click "✋ Available" - sends message
- [ ] Click "📊 Status" - sends message
- [ ] Click "🚑 Help" - sends message

---

## 4️⃣ Test System Insights

```bash
curl http://localhost:5000/system-insights
```

**Expected Response:**
- [ ] Status 200
- [ ] `metrics` object with:
  - [ ] `success_rate`
  - [ ] `avg_match_time_minutes`
  - [ ] `donor_acceptance_rate`
  - [ ] `avg_donor_response_time`
- [ ] `agent_performance` array

---

## 5️⃣ Test Complete Workflow

### Create Blood Request

```bash
curl -X POST http://localhost:5000/create-request -H "Content-Type: application/json" -d "{\"patientName\":\"Test Patient\",\"blood\":\"O+\",\"hospital\":\"Test Hospital\",\"latitude\":10.5276,\"longitude\":76.2144,\"user_id\":1}"
```

**Expected:**
- [ ] Status 200
- [ ] Donor matched
- [ ] Notification sent
- [ ] Urgency level assigned

### Check Database

```sql
SELECT * FROM requests ORDER BY created_at DESC LIMIT 1;
```

**Expected:**
- [ ] New request created
- [ ] `urgency` field populated
- [ ] `agent_analysis` field has JSON

```sql
SELECT * FROM notifications ORDER BY created_at DESC LIMIT 1;
```

**Expected:**
- [ ] Notification created
- [ ] `message` field has personalized text
- [ ] `status` = 'sent'

```sql
SELECT * FROM agent_decisions ORDER BY created_at DESC LIMIT 1;
```

**Expected:**
- [ ] Decision logged
- [ ] `agent_type` present
- [ ] `confidence` score present

---

## 6️⃣ Test Demo Script

```bash
python demo_agentic_chatbot.py
```

**Expected:**
- [ ] Script runs without errors
- [ ] All 6 demo sections execute
- [ ] API responses received
- [ ] Data displayed correctly

---

## 7️⃣ Test Error Handling

### Invalid Message

```bash
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d "{\"user_id\":1,\"message\":\"\"}"
```

**Expected:**
- [ ] Status 400
- [ ] Error message: "Message is required"

### Missing User ID

```bash
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d "{\"message\":\"test\"}"
```

**Expected:**
- [ ] Handles gracefully (user_id can be None)

### Backend Not Running

- [ ] chatbot.html shows connection error
- [ ] Error message is user-friendly

---

## 8️⃣ Test Background Monitoring

### Wait 5 Minutes

After creating a request, wait 5 minutes and check logs.

**Expected in console:**
- [ ] No errors
- [ ] Monitoring checks running
- [ ] (If request pending 10+ min) Auto-retry triggered

### Check Escalation Log

```sql
SELECT * FROM escalation_log ORDER BY created_at DESC;
```

**Expected:**
- [ ] Escalation actions logged (if any triggered)
- [ ] `action`, `reason`, `result` fields populated

---

## 9️⃣ Test Learning System

### Simulate Donor Response

```bash
curl -X POST http://localhost:5000/donor-response -H "Content-Type: application/json" -d "{\"notification_id\":1,\"response\":\"accepted\",\"response_time\":300}"
```

**Expected:**
- [ ] Status 200
- [ ] Response recorded
- [ ] Pattern updated in database

### Check Donor Patterns

```sql
SELECT * FROM donor_patterns ORDER BY updated_at DESC LIMIT 1;
```

**Expected:**
- [ ] Pattern entry exists
- [ ] `response_count` incremented
- [ ] `avg_response_time` updated
- [ ] `acceptance_rate` calculated

---

## 🔟 Performance Tests

### Response Time

- [ ] Chat endpoint responds < 5 seconds
- [ ] NLP parsing < 3 seconds
- [ ] Donor matching < 2 seconds

### Concurrent Requests

Send 5 requests simultaneously:

```bash
for i in {1..5}; do
  curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d "{\"user_id\":$i,\"message\":\"Need O+ blood\"}" &
done
```

**Expected:**
- [ ] All requests handled
- [ ] No errors
- [ ] Responses within reasonable time

---

## 🎯 Final Verification

### All Core Features Working

- [ ] Natural language understanding
- [ ] Autonomous donor matching
- [ ] Automatic notifications
- [ ] Background monitoring
- [ ] Auto-escalation logic
- [ ] Donor conversation handling
- [ ] Emergency guidance
- [ ] Status tracking
- [ ] Pattern learning
- [ ] Web interface

### Documentation Complete

- [ ] README.md updated
- [ ] IMPLEMENTATION_SUMMARY.md created
- [ ] CHATBOT_QUICKSTART.md created
- [ ] AGENTIC_CHATBOT_README.md created
- [ ] AGENTIC_COMPARISON.md created

### Demo Ready

- [ ] Backend starts without errors
- [ ] Chatbot.html works
- [ ] Demo script runs
- [ ] All features demonstrable

---

## 🐛 Common Issues & Fixes

### Issue: "ANTHROPIC_API_KEY not set"
**Fix:** 
```bash
set ANTHROPIC_API_KEY=your_key_here
```

### Issue: "Table doesn't exist"
**Fix:**
```bash
python database.py
python add_escalation_table.py
```

### Issue: "Connection refused"
**Fix:**
- Check backend is running on port 5000
- Check firewall settings

### Issue: "No donors found"
**Fix:**
- Add test donors to database
- Run `add_sample_data.py`

### Issue: "Chatbot not responding"
**Fix:**
- Check browser console (F12)
- Verify API_URL in chatbot.html
- Check CORS is enabled

---

## ✅ Sign-Off

**Tested by:** _______________  
**Date:** _______________  
**Status:** _______________  

**All tests passed?** [ ] YES [ ] NO

**Ready for demo?** [ ] YES [ ] NO

**Ready for hackathon?** [ ] YES [ ] NO

---

## 📝 Notes

Use this space to note any issues or observations:

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

**If all checkboxes are checked, you're ready to win! 🏆**
