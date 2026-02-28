import requests
import json

url = "http://localhost:5000/ai-chat"
data = {
    "message": "What are the eligibility requirements for blood donation?",
    "history": []
}

print("Testing AI chat endpoint...")
print(f"Sending request to: {url}")
print(f"Message: {data['message']}\n")

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {str(e)}")
