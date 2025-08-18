from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from .keys import s, model

# ✅ Setup LLM (Gemini)
llm = ChatGoogleGenerativeAI(
    model=model,
    google_api_key=s,
    temperature=0.2
)

# Mock tool: critique responses
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

# --- Conversation history (manual) ---
chat_history = []

# --- Critic-specific system prompt ---
critic_prompt = (
    "You are a Critic Agent. Your goal is to audit disaster response plans, "
    "identify unsafe decisions or errors, and provide constructive feedback. "
    "You can use the Plan Auditor tool to check details if necessary.\n"
)

# print("🧐 Chat with Critic Agent (type 'exit' to quit)\n")
# print("Role: Critic")
# print("Goal: Audit disaster response plans and identify unsafe errors\n")

# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("👋 Exiting...")
#         break

#     # Prepend conversation history + Critic prompt
#     context = "\n".join(chat_history)
#     full_input = f"{critic_prompt}\nConversation so far:\n{context}\nUser: {user_input}"

#     try:
#         response = critic.run(full_input)
#         print(f"\nCritic: {response}\n")
#         # Store exchange in history
#         chat_history.append(f"User: {user_input}")
#         chat_history.append(f"Critic: {response}")
#     except Exception as e:
#         print(f"⚠️ Error: {e}\n")
