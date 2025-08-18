from google import genai
from keys import s,model   # API key stored in keys.py

# Initialize client
client = genai.Client(api_key=s)

print("💬 GPT-5 Chat (type 'quit' to exit)\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("👋 Goodbye from GPT-5!")
        break

    # Send prompt to Gemini (renamed as GPT-5)
    response = client.models.generate_content(
        model=model,
        contents=user_input
    )

    print("GPT-5:", response.text)
