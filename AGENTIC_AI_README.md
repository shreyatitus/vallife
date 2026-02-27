# LifeLink - Agentic AI Blood Donation Network 🤖❤️

## Competition-Ready Autonomous Multi-Agent System

LifeLink is an **AI-powered emergency blood donation platform** featuring a sophisticated **multi-agent architecture** that autonomously coordinates blood requests, matches donors, and learns from interactions.

---

## 🎯 Agentic AI Capabilities

### 1. **Multi-Agent Architecture**
- **Coordinator Agent**: Analyzes requests using LLM, determines urgency, creates strategic action plans
- **Matcher Agent**: Predictive donor matching with multi-criteria optimization and learning
- **Communication Agent**: Generates personalized messages using AI for each donor
- **Monitor Agent**: Autonomous monitoring, triggers retry logic, tracks performance
- **NLP Agent**: Processes natural language blood requests

### 2. **Autonomous Decision Making**
- ✅ AI analyzes request context and urgency without human intervention
- ✅ Multi-criteria donor scoring (distance, availability, history, response patterns)
- ✅ Dynamic strategy adjustment based on urgency level
- ✅ Autonomous retry with alternative donors when primary declines
- ✅ Self-triggered escalation for stalled requests

### 3. **Predictive Intelligence**
- 📊 Learns donor response patterns over time
- 📊 Predicts donor availability based on historical data
- 📊 Time-based optimization (preferred response times)
- 📊 Confidence scoring for all agent decisions

### 4. **Natural Language Processing**
- 💬 Parse unstructured blood requests: *"URGENT! Need O+ blood at City Hospital"*
- 💬 Extract patient info, blood type, urgency, location from text
- 💬 Intelligent urgency detection from language patterns

### 5. **Adaptive Learning**
- 🧠 Tracks donor response rates and times
- 🧠 Updates availability predictions after each interaction
- 🧠 Learns preferred contact times for each donor
- 🧠 Improves matching accuracy over time

### 6. **Autonomous Monitoring & Actions**
- ⚡ Monitors pending requests every 5 minutes
- ⚡ Auto-expands search radius if no responses
- ⚡ Escalates to blood banks after multiple failed attempts
- ⚡ Generates follow-up messages autonomously

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Agent Orchestrator                      │
│         (Coordinates all autonomous agents)              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        │            │            │              │
   ┌────▼───┐  ┌────▼────┐  ┌───▼────┐   ┌─────▼─────┐
   │Coordin-│  │ Matcher │  │Communi-│   │  Monitor  │
   │  ator  │  │  Agent  │  │ cation │   │   Agent   │
   │ Agent  │  │         │  │ Agent  │   │           │
   └────┬───┘  └────┬────┘  └───┬────┘   └─────┬─────┘
        │           │           │              │
        └───────────┴───────────┴──────────────┘
                     │
              ┌──────▼──────┐
              │  Database   │
              │  + Patterns │
              └─────────────┘
```

---

## 🚀 Key Features for Competition

### **1. Intelligent Request Analysis**
```python
# AI analyzes: "URGENT! Accident victim needs A+ blood at Memorial Hospital"
→ Urgency: CRITICAL
→ Context: Trauma case, time-sensitive
→ Action Plan: Contact top 3 donors simultaneously, prepare backup
→ Confidence: 92%
```

### **2. Multi-Criteria Donor Matching**
```python
Scoring Algorithm:
- Distance Score (0-1): Proximity to hospital
- Availability Score (0-1): Predicted response likelihood
- History Score (0-1): Past donation experience
- Weighted by urgency level (critical/high/medium/low)
```

### **3. Personalized AI Communication**
```
Generated Message Example:
"Hi John, your past 3 donations have saved lives. An accident victim 
2.3km from you urgently needs A+ blood at Memorial Hospital. Your quick 
response could be life-saving. Can you help? Reply YES to confirm."
```

### **4. Autonomous Retry Logic**
```
Timeline:
T+0:   Primary donor contacted
T+15:  No response → Auto-contact backup donor #1
T+30:  Still pending → Auto-contact backup donor #2
T+45:  Multiple failures → Escalate to blood banks
```

### **5. Learning & Adaptation**
```python
Donor Pattern Learning:
- Response Rate: 85% → Adjusts availability score
- Avg Response Time: 12 minutes → Optimizes timing
- Preferred Time: 9AM-5PM → Schedules accordingly
- Acceptance History: 7/8 → High priority in matching
```

---

## 📊 Database Schema (Enhanced)

### New Tables for AI Agents:
- **agent_decisions**: Logs all AI decisions with reasoning and confidence
- **donor_patterns**: Stores learned behavior patterns for each donor
- **notifications**: Enhanced with response_time and AI-generated messages

---

## 🎮 API Endpoints

### **Agentic AI Endpoints:**

#### 1. Natural Language Request
```bash
POST /nlp-request
{
  "text": "Emergency! Need B+ blood for surgery patient at City Hospital",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

#### 2. AI-Powered Request Processing
```bash
POST /create-request
# Returns: AI analysis, matched donor, availability score, backup count
```

#### 3. Donor Response Learning
```bash
POST /donor-response
{
  "notification_id": 123,
  "response": "accepted",
  "response_time": 300
}
# Triggers: Pattern learning + Autonomous retry if declined
```

#### 4. System Insights
```bash
GET /system-insights
# Returns: Success metrics, agent performance, optimization insights
```

#### 5. Autonomous Monitoring
```bash
POST /autonomous-monitor
# Triggers: Auto-retry for stalled requests, escalation logic
```

---

## 🧪 Demo Script

Run the comprehensive demo:
```bash
python demo_agents.py
```

**Demonstrates:**
1. ✅ Natural language processing
2. ✅ Intelligent multi-criteria matching
3. ✅ Autonomous monitoring & retry
4. ✅ AI-driven performance insights
5. ✅ Adaptive learning capabilities

---

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
cd valkyire/lifelink_backend/lifelink_backend
pip install -r requirements.txt
```

### 2. Set API Key
```bash
# Windows
set ANTHROPIC_API_KEY=your_api_key_here

# Linux/Mac
export ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Initialize Database
```bash
python database.py
```

### 4. Run Backend
```bash
python app.py
```

### 5. Run Demo
```bash
python demo_agents.py
```

---

## 🏆 Competition Advantages

### **Why This System Wins:**

1. **True Agentic Behavior**
   - Agents make autonomous decisions without human intervention
   - Multi-step reasoning and planning
   - Self-triggered actions based on monitoring

2. **Learning & Adaptation**
   - System improves with every interaction
   - Predictive analytics for donor availability
   - Pattern recognition for optimization

3. **Real-World Impact**
   - Solves critical healthcare problem
   - Measurable outcomes (lives saved)
   - Scalable to blood banks and hospitals

4. **Advanced AI Integration**
   - LLM-powered analysis and communication
   - Natural language understanding
   - Context-aware decision making

5. **Comprehensive Architecture**
   - Multiple specialized agents
   - Coordinated workflows
   - Robust error handling and fallbacks

---

## 📈 Performance Metrics

The system tracks:
- **Success Rate**: % of requests fulfilled
- **Average Match Time**: Minutes to find donor
- **Donor Acceptance Rate**: % of contacted donors who accept
- **Agent Confidence**: Average confidence in decisions
- **Response Patterns**: Learned donor behaviors

---

## 🔮 Future Enhancements

- Voice-based request processing
- Real-time traffic-aware routing
- Blood bank inventory integration
- Multi-language support
- Mobile app with push notifications
- Blockchain for donation tracking

---

## 📝 Technical Stack

**Backend:**
- Python + Flask
- Anthropic Claude (LLM)
- MySQL Database

**AI/ML:**
- Multi-agent orchestration
- Predictive modeling
- Natural language processing
- Reinforcement learning (pattern updates)

**Frontend:**
- HTML/CSS/JavaScript
- Real-time updates

---

## 👥 Team

Built for Agentic AI Competition

---

## 📄 License

MIT License

---

## 🎯 Conclusion

LifeLink demonstrates **production-ready agentic AI** with:
- ✅ Autonomous multi-agent coordination
- ✅ Intelligent decision making with reasoning
- ✅ Continuous learning and adaptation
- ✅ Real-world healthcare impact
- ✅ Scalable architecture

**This is not just AI-assisted—it's AI-driven autonomous action.**
