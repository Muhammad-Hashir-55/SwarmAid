from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from keys import s, model

# ✅ Setup LLM (Gemini)
llm = ChatGoogleGenerativeAI(
    model=model,
    google_api_key=s,
    temperature=0.2
)

# Mock tool for route optimization (later replace with OSMnx)
def optimize_routes(query: str) -> str:
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

# --- Conversation history (manual) ---
chat_history = []

print("🚚 Chat with Logistics Manager Agent (type 'exit' to quit)\n")
print("Role: Logistics Manager")
print("Goal: Plan safe and efficient supply routes\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Exiting...")
        break

    # Prepend conversation history
    context = "\n".join(chat_history)
    full_input = f"Conversation so far:\n{context}\nUser: {user_input}"

    try:
        response = logistics_manager.run(full_input)
        print(f"\nLogistics Manager: {response}\n")
        # Store exchange in history
        chat_history.append(f"User: {user_input}")
        chat_history.append(f"Logistics Manager: {response}")
    except Exception as e:
        print(f"⚠️ Error: {e}\n")
