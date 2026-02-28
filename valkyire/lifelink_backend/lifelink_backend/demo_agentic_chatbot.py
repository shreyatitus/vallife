import requests
import time
import json

API_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def demo_chatbot():
    """Demo the agentic chatbot capabilities"""
    
    print_section("🤖 LIFELINK AGENTIC AI DEMO")
    print("This demo showcases TRUE agentic behavior:")
    print("✓ Autonomous decision making")
    print("✓ Multi-step reasoning")
    print("✓ Self-triggered actions")
    print("✓ Continuous monitoring")
    print("✓ Adaptive learning\n")
    
    input("Press Enter to start demo...")
    
    # Demo 1: Natural Language Blood Request
    print_section("1️⃣ SMART EMERGENCY INTAKE (Natural Language)")
    
    messages = [
        "URGENT! Need O+ blood at City Hospital, accident victim",
        "Emergency! Patient needs A- blood for surgery at Memorial Hospital",
        "Need B+ blood urgently"
    ]
    
    for msg in messages:
        print(f"\n👤 User: {msg}")
        
        response = requests.post(f"{API_URL}/chat", json={
            "user_id": 1,
            "message": msg,
            "latitude": 10.5276,
            "longitude": 76.2144
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n🤖 AI Response:")
            print(data.get('reply', 'No response'))
            print(f"\n📊 Actions Taken: {', '.join(data.get('actions', []))}")
            
            if data.get('parsed'):
                print(f"\n🔍 Extracted Data:")
                print(f"   Blood Type: {data['parsed'].get('bloodType')}")
                print(f"   Urgency: {data['parsed'].get('urgency')}")
                print(f"   Hospital: {data['parsed'].get('hospital')}")
        
        time.sleep(2)
    
    input("\nPress Enter to continue...")
    
    # Demo 2: Auto Donor Matching
    print_section("2️⃣ AUTO DONOR MATCHING & NOTIFICATION")
    
    print("Creating blood request...")
    response = requests.post(f"{API_URL}/create-request", json={
        "patientName": "John Doe",
        "blood": "O+",
        "hospital": "City Hospital",
        "latitude": 10.5276,
        "longitude": 76.2144,
        "user_id": 1
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ {data.get('message')}")
        print(f"\n📊 AI Analysis:")
        print(f"   Urgency Level: {data.get('urgency')}")
        print(f"   Availability Score: {data.get('availability_score', 0):.0%}")
        print(f"   Backup Donors: {data.get('backup_donors', 0)}")
        
        if data.get('analysis'):
            analysis = data['analysis']
            print(f"\n🧠 AI Reasoning:")
            print(f"   {analysis.get('reasoning', 'N/A')}")
    
    input("\nPress Enter to continue...")
    
    # Demo 3: Autonomous Monitoring
    print_section("3️⃣ AUTONOMOUS MONITORING & AUTO-RETRY")
    
    print("Triggering autonomous monitoring system...")
    response = requests.post(f"{API_URL}/autonomous-monitor")
    
    if response.status_code == 200:
        data = response.json()
        actions = data.get('actions_taken', [])
        
        if actions:
            print(f"\n🔄 Autonomous Actions Taken: {len(actions)}")
            for action in actions:
                print(f"   • {action.get('status')}: Request {action.get('request_id', 'N/A')}")
        else:
            print("\n✓ All requests are being handled properly")
            print("  (Auto-retry triggers after 10 min of no response)")
    
    input("\nPress Enter to continue...")
    
    # Demo 4: System Insights
    print_section("4️⃣ AI-DRIVEN SYSTEM INSIGHTS")
    
    response = requests.get(f"{API_URL}/system-insights")
    
    if response.status_code == 200:
        data = response.json()
        metrics = data.get('metrics', {})
        
        print("📈 Performance Metrics:")
        print(f"   Success Rate: {metrics.get('success_rate', 0):.1%}")
        print(f"   Avg Match Time: {metrics.get('avg_match_time_minutes', 0):.1f} minutes")
        print(f"   Donor Acceptance: {metrics.get('donor_acceptance_rate', 0):.1%}")
        print(f"   Avg Response Time: {metrics.get('avg_donor_response_time', 0):.0f} seconds")
        
        print("\n🤖 Agent Performance:")
        for agent in data.get('agent_performance', []):
            print(f"   {agent['agent_type']}: {agent['avg_confidence']:.1%} confidence ({agent['decision_count']} decisions)")
    
    input("\nPress Enter to continue...")
    
    # Demo 5: Conversational Interactions
    print_section("5️⃣ CONVERSATIONAL AI INTERACTIONS")
    
    conversations = [
        "I am available to donate blood",
        "Check my request status",
        "What should I do in case of heavy bleeding?",
        "How does LifeLink work?"
    ]
    
    for msg in conversations:
        print(f"\n👤 User: {msg}")
        
        response = requests.post(f"{API_URL}/chat", json={
            "user_id": 1,
            "message": msg
        })
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get('reply', 'No response')
            # Print first 200 chars
            print(f"\n🤖 AI: {reply[:200]}{'...' if len(reply) > 200 else ''}")
        
        time.sleep(1)
    
    # Demo 6: Escalation Stats
    print_section("6️⃣ AUTO-ESCALATION STATISTICS")
    
    response = requests.get(f"{API_URL}/escalation-stats")
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get('stats', [])
        
        if stats:
            print("📊 Recent Escalation Actions:")
            for stat in stats[:5]:
                print(f"   {stat['date']}: {stat['action']} ({stat['count']} times)")
        else:
            print("✓ No escalations needed - system running smoothly!")
    
    print_section("✅ DEMO COMPLETE")
    print("\n🎯 Key Agentic Features Demonstrated:")
    print("   1. Natural language understanding")
    print("   2. Autonomous donor matching")
    print("   3. Self-triggered monitoring")
    print("   4. Intelligent decision making")
    print("   5. Conversational interactions")
    print("   6. Auto-escalation logic")
    print("\n💡 This is TRUE Agentic AI - not just a chatbot!")
    print("\n🌐 Open chatbot.html in browser for interactive demo")

if __name__ == "__main__":
    try:
        # Test connection
        response = requests.get(f"{API_URL}/system-insights", timeout=2)
        demo_chatbot()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Backend not running!")
        print("\nPlease start the backend first:")
        print("   cd valkyire/lifelink_backend/lifelink_backend")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")
