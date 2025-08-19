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
def critique_plan(query: str) -> str:
    return f"(Critique: Checked plan for unsafe routes or errors in {query})"

tools = [
    Tool(
        name="Plan Auditor",
        func=critique_plan,
        description="Audit disaster response plans and catch unsafe errors"
    )
]

# ✅ Build Critic Agent
critic = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True
)

# --- Optional Critic prompt (system-level role description) ---
critic_prompt = (
    "You are a Critic Agent. Your goal is to audit disaster response plans, "
    "identify unsafe decisions or errors, and provide constructive feedback. "
    "You can use the Plan Auditor tool to check details if necessary.\n"
)

# # --- Optional interactive loop ---
# print("🧐 Chat with Critic Agent (type 'exit' to quit)\n")
# print("Role: Critic")
# print("Goal: Audit disaster response plans and identify unsafe errors\n")
#
# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("👋 Exiting...")
#         break
#
#     full_input = f"{critic_prompt}\nUser: {user_input}"
#
#     try:
#         response = critic.run(full_input)
#         print(f"\nCritic: {response}\n")
#     except OutputParserException as e:
#         print(f"\n⚠️ Parsing issue, showing raw LLM response:\n{str(e)}\n")
#         try:
#             raw_response = llm.invoke(user_input)
#             print(f"Critic (raw): {raw_response.content}\n")
#         except Exception as inner_e:
#             print(f"❌ Fallback also failed: {inner_e}\n")
#     except Exception as e:
#         print(f"⚠️ Unexpected error: {e}\n")
