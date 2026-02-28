"""
Demo: Agentic AI Blood Donation System
Exact Workflow Demonstration
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def demo_workflow():
    print("\n" + "="*70)
    print("🤖 AGENTIC AI WORKFLOW DEMONSTRATION")
    print("="*70)
    
    # Step 1: User creates blood request
    print("\n📝 STEP 1: User creates blood request")
    print("-" * 70)
    
    request_data = {
        "patientName": "John Doe",
        "blood": "O+",
        "hospital": "City Hospital",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    print(f"Request Details:")
    print(f"  Patient: {request_data['patientName']}")
    print(f"  Blood Type: {request_data['blood']}")
    print(f"  Hospital: {request_data['hospital']}")
    
    # Step 2-7: AI Agent processes automatically
    print("\n🤖 STEP 2-7: AI Agent Processing...")
    print("-" * 70)
    
    response = requests.post(f"{BASE_URL}/create-request", json=request_data)
    result = response.json()
    
    if result.get('donor'):
        print(f"\n✅ SUCCESS!")
        print(f"  ✓ Filtered donors by blood group: {request_data['blood']}")
        print(f"  ✓ Checked cooldown eligibility (90 days)")
        print(f"  ✓ Calculated distances using Haversine formula")
        print(f"  ✓ Ranked donors by proximity")
        print(f"  ✓ Notified top donor")
        print(f"\n📍 Matched Donor:")
        print(f"  Name: {result['donor']['name']}")
        print(f"  Distance: {result['donor']['distance']} km")
        print(f"  Phone: {result['donor']['phone']}")
        print(f"  Backup Donors Available: {result['backup_donors']}")
        
        notification_id = result['notification_id']
        
        # Step 8: Simulate donor declining
        print("\n❌ STEP 8: Donor Declined - AI Auto-Retry")
        print("-" * 70)
        time.sleep(2)
        
        decline_response = requests.post(f"{BASE_URL}/donor-response", json={
            "notification_id": notification_id,
            "response": "declined"
        })
        
        retry_result = decline_response.json()
        
        if retry_result.get('status') == 'retry_sent':
            print(f"\n🔄 AI AUTOMATICALLY CONTACTED NEXT DONOR:")
            print(f"  Name: {retry_result['donor']['name']}")
            print(f"  Distance: {retry_result['donor']['distance']} km")
            print(f"  Attempt: #{retry_result['attempt']}")
            print(f"\n✅ Autonomous retry successful!")
        
    else:
        print(f"\n❌ {result.get('message')}")
        print(f"   Failed at step: {result.get('step_failed')}")
    
    print("\n" + "="*70)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Autonomous AI agent activation")
    print("  ✓ Multi-step filtering and ranking")
    print("  ✓ Distance-based optimization")
    print("  ✓ Automatic retry on decline")
    print("  ✓ No human intervention required")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        demo_workflow()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Backend server is running (python app_simple.py)")
        print("  2. Database is initialized")
        print("  3. Test donors are registered")
