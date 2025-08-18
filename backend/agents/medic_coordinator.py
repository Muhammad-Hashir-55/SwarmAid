from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from .keys import s, model

# ✅ Setup LLM (Gemini)
llm = ChatGoogleGenerativeAI(
    model=model,
    google_api_key=s,
    temperature=0.2
)

# Mock tool for triage (later replace with Twitter API)
def analyze_tweets(query: str) -> str:
    return f"(Pretend triage from tweets: {query})"

tools = [
    Tool(
        name="Tweet Analyzer",
        func=analyze_tweets,
        description="Analyze Twitter hashtags for medical triage info"
    )
]

# ✅ Build Medic Coordinator Agent (without LangChain memory)
medic_coordinator = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True
)

# --- Conversation history (manual) ---
chat_history = []

# print("🚑 Chat with Medic Coordinator Agent (type 'exit' to quit)\n")
# print("Role: Emergency Medic Coordinator")
# print("Goal: Use social media (Twitter) signals to assist in medical triage\n")

# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("👋 Exiting...")
#         break

#     # prepend conversation history
#     context = "\n".join(chat_history)
#     full_input = f"Conversation so far:\n{context}\nUser: {user_input}"

#     try:
#         response = medic_coordinator.run(full_input)
#         print(f"\nMedic Coordinator: {response}\n")
#         # store exchange in history
#         chat_history.append(f"User: {user_input}")
#         chat_history.append(f"Medic Coordinator: {response}")
#     except Exception as e:
#         print(f"⚠️ Error: {e}\n")
