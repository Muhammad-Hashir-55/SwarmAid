from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI  # ✅ Use AIML API wrapper (compatible with OpenAI SDK)
from langchain.schema import OutputParserException
import os
from .keys import ss # remember if you are testing in this file then remove . from .keys to use while loop

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
def analyze_satellite_data(query: str) -> str:
    return f"(Pretend analysis of satellite data: {query})"

tools = [
    Tool(
        name="Satellite Analyzer",
        func=analyze_satellite_data,
        description="Use this to analyze satellite imagery or geospatial queries"
    )
]

# ✅ Build Agent
data_analyst = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True
)

# # --- Interactive loop ---
# print("🚀 Chat with Data Analyst Agent (type 'exit' to quit)\n")
# print("Role: Senior Geospatial Analyst")
# print("Goal: Identify disaster impact zones using satellite data")
# print("Backstory: Expert in remote sensing and disaster assessment\n")

# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("👋 Exiting...")
#         break

#     try:
#         response = data_analyst.run(user_input)
#         print(f"\nData Analyst: {response}\n")
#     except OutputParserException as e:
#         # fallback: return raw LLM output instead of crashing
#         print(f"\n⚠️ Parsing issue, showing raw LLM response:\n{str(e)}\n")
#         try:
#             raw_response = llm.invoke(user_input)
#             print(f"Data Analyst (raw): {raw_response.content}\n")
#         except Exception as inner_e:
#             print(f"❌ Fallback also failed: {inner_e}\n")
#     except Exception as e:
#         print(f"⚠️ Unexpected error: {e}\n")
