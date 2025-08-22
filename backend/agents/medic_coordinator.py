# agents/medic_coordinator.py
from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
from geopy.geocoders import Nominatim
# from .keys import ss, api_key, api_key_secret, access_token, access_token_secret
import tweepy
import re
import os



# # ✅ Load AIML API key
# AIML_API_KEY = ss


######################################
from dotenv import load_dotenv

# ✅ Load .env file
load_dotenv()

# ✅ Read AIML API key
AIML_API_KEY = os.getenv("ss")
api_key = os.getenv("api_key")
api_key_secret = os.getenv("api_key_secret")
access_token = os.getenv("access_token")
access_token_secret = os.getenv("access_token_secret")

########################################



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

def _geocode(place: str):
    geolocator = Nominatim(user_agent="swarm-aid")
    try:
        loc = geolocator.geocode(place, timeout=5)
    except Exception:
        loc = None
    if not loc:
        return None
    return (loc.latitude, loc.longitude)

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

        joined = "\n".join(texts[:5])
        summary = llm.invoke(
            f"Summarize urgent medical needs based on these tweets:\n{joined}"
        )
        return summary.content

    except Exception as e:
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

# ---------------- GeoJSON overlay (NEW) ----------------
def compute_triage_features(scenario: str):
    """
    Generates triage cluster points near the scenario using tweet-derived summary.
    Returns: {"features": [...], "summary": "..."}
    """
    loc = _geocode(scenario)
    if not loc:
        return {"features": [], "summary": f"Could not geocode location from '{scenario}'."}

    lat, lon = loc

    # 1) Get text summary from social signals
    summary_text = analyze_tweets(f"{scenario} disaster medical injuries hospitals damage")
    text_lower = summary_text.lower()

    # 2) Heuristic tag → severity + label
    buckets = []
    if re.search(r"\bburn(s| units| care)?\b", text_lower):
        buckets.append(("Triage: Burns", "severe", +0.03, +0.01))
    if re.search(r"\b(crush|fracture|orthopedic)\b", text_lower):
        buckets.append(("Triage: Ortho/Crush", "moderate", -0.04, +0.02))
    if re.search(r"\b(dehydration|children|pediatric)\b", text_lower):
        buckets.append(("Triage: Pediatric/Dehydration", "moderate", +0.02, -0.03))
    if re.search(r"\b(overwhelmed|icu|casualties|mass casualty)\b", text_lower):
        buckets.append(("Triage: Casualty Surge", "severe", -0.03, -0.02))

    # Default if nothing matched
    if not buckets:
        buckets = [
            ("Triage: Central Intake", "moderate", +0.02, +0.02),
            ("Triage: Field Stabilization", "moderate", -0.03, -0.01),
        ]

    # 3) Build features (Points only to match your frontend)
    features = []
    for name, severity, dx, dy in buckets[:4]:
        features.append({
            "type": "Feature",
            "properties": {"name": name, "severity": severity},
            "geometry": {"type": "Point", "coordinates": [lon + dx, lat + dy]},
        })

    # 4) Short map-oriented summary
    map_summary = (
        "Triage clusters placed near incident center based on social-signal summary: "
        + ", ".join([f"{n} ({s})" for n, s, *_ in buckets[:4]])
        + ". Use these as intake/stabilization anchors; connect to Logistics routes."
    )

    return {"features": features, "summary": map_summary, "source_summary": summary_text}

# ---------------- Tools & Agent ----------------
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
