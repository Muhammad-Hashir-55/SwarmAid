from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI  # ✅ AIML API wrapper
from langchain.schema import OutputParserException
from .keys import ss   # ✅ AIML API key

# ✅ Load AIML API key
AIML_API_KEY = ss

# ✅ Setup LLM (GPT-5 via AIML API)
llm = ChatOpenAI(
    model="gpt-5-chat-latest",
    api_key=AIML_API_KEY,
    base_url="https://api.aimlapi.com/v1",
    temperature=0.2
)

# --- Define tools ---
def analyze_tweets(query: str) -> str:
    # 🔹 Placeholder for now, later integrate real Twitter API / cached JSON
    return f"(Pretend triage from tweets: {query})"

tools = [
    Tool(
        name="Tweet Analyzer",
        func=analyze_tweets,
        description="Analyze Twitter hashtags for medical triage info"
    )
]

# ✅ Build Medic Coordinator Agent
medic_coordinator = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True
)

# # --- Optional interactive loop ---
# print("🚑 Chat with Medic Coordinator Agent (type 'exit' to quit)\n")
# print("Role: Emergency Medic Coordinator")
# print("Goal: Use social media (Twitter/X signals) to assist in medical triage\n")
#
# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("👋 Exiting...")
#         break
#
#     try:
#         response = medic_coordinator.run(user_input)
#         print(f"\nMedic Coordinator: {response}\n")
#     except OutputParserException as e:
#         print(f"\n⚠️ Parsing issue, showing raw LLM response:\n{str(e)}\n")
#         try:
#             raw_response = llm.invoke(user_input)
#             print(f"Medic Coordinator (raw): {raw_response.content}\n")
#         except Exception as inner_e:
#             print(f"❌ Fallback also failed: {inner_e}\n")
#     except Exception as e:
#         print(f"⚠️ Unexpected error: {e}\n")
