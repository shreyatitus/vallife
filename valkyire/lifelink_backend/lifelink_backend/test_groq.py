from groq import Groq

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

print("Testing Groq API...")

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ],
        temperature=0.7,
        max_tokens=100
    )
    print("SUCCESS!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"ERROR: {str(e)}")
