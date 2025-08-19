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
def optimize_routes(query: str) -> str:
    # 🔹 Placeholder for now, later replace with OSMnx
    return f"(Pretend optimized supply route avoiding hazards for: {query})"

tools = [
    Tool(
        name="Route Optimizer",
        func=optimize_routes,
        description="Optimize supply routes while avoiding hazards"
    )
]

# ✅ Build Logistics Manager Agent
logistics_manager = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True
)

# # --- Optional interactive loop ---
# print("🚚 Chat with Logistics Manager Agent (type 'exit' to quit)\n")
# print("Role: Logistics Manager")
# print("Goal: Plan safe and efficient supply routes\n")
#
# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("👋 Exiting...")
#         break
#
#     try:
#         response = logistics_manager.run(user_input)
#         print(f"\nLogistics Manager: {response}\n")
#     except OutputParserException as e:
#         print(f"\n⚠️ Parsing issue, showing raw LLM response:\n{str(e)}\n")
#         try:
#             raw_response = llm.invoke(user_input)
#             print(f"Logistics Manager (raw): {raw_response.content}\n")
#         except Exception as inner_e:
#             print(f"❌ Fallback also failed: {inner_e}\n")
#     except Exception as e:
#         print(f"⚠️ Unexpected error: {e}\n")
