from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
from .keys import ss, api_key, api_key_secret, access_token, access_token_secret
import tweepy

# ✅ Load AIML API key
AIML_API_KEY = ss

# ✅ Setup LLM (GPT-5 via AIML API)
llm = ChatOpenAI(
    model="gpt-5-chat-latest",
    api_key=AIML_API_KEY,
    base_url="https://api.aimlapi.com/v1",
    temperature=0.2
)

# --- Setup Twitter Tweepy Client ---
auth = tweepy.OAuth1UserHandler(
    api_key, api_key_secret,
    access_token, access_token_secret
)
api = tweepy.API(auth, wait_on_rate_limit=True)

# --- Tweet Analyzer function ---
def analyze_tweets(query: str) -> str:
    """
    Search Twitter (X) using Tweepy and summarize disaster-related tweets.
    Falls back to demo tweets if API fails.
    """
    try:
        tweets = api.search_tweets(
            q=query + " -filter:retweets AND -filter:replies",
            lang="en",
            count=5,
            tweet_mode="extended"
        )

        texts = [tweet.full_text for tweet in tweets]
        if not texts:
            raise ValueError("No tweets found.")

        print(f"📡 Retrieved {len(texts)} live tweets for query: {query}")
        for t in texts:
            print("📝 Tweet:", t[:100], "...")  # show first 100 chars

        # Take first 5 for summarization
        joined = "\n".join(texts[:5])
        summary = llm.invoke(
            f"Summarize urgent medical needs based on these tweets:\n{joined}"
        )
        print("✅ Using live Twitter data")
        return summary.content

    except Exception as e:
        print(f"🛑 Fallback triggered due to: {e}")

        # 🚑 Fallback dataset
        fallback_tweets = [
            "Central hospitals overwhelmed with casualties.",
            "Eastern districts need urgent trauma care and burn units.",
            "Shortage of ambulances delaying medical response.",
            "Rescue workers report crush injuries and fractures.",
            "Children suffering shock and dehydration in shelters."
        ]
        joined = "\n".join(fallback_tweets)
        summary = llm.invoke(
            f"(Twitter API unavailable: {e}) Summarize urgent medical needs based on these sample tweets:\n{joined}"
        )
        return summary.content


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

# # --- Local interactive test ---
# if __name__ == "__main__":
#     print("🚑 Chat with Medic Coordinator Agent (type 'exit' to quit)\n")

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             print("👋 Exiting...")
#             break
#         try:
#             print("🔎 Checking Twitter for live tweets...")
#             response = medic_coordinator.run(user_input)
#             print(f"\nMedic Coordinator: {response}\n")
#         except Exception as e:
#             print(f"⚠️ Error: {e}\n")
