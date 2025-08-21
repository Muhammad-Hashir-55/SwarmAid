# agents/data_analyst.py
from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
from geopy.geocoders import Nominatim
from math import radians, sin, cos, asin, sqrt
import requests
import os
import datetime as dt

from .keys import ss  # AIML API key for ChatOpenAI (AIML API wrapper)

AIML_API_KEY = ss

llm = ChatOpenAI(
    model="gpt-5-chat-latest",
    api_key=AIML_API_KEY,
    base_url="https://api.aimlapi.com/v1",
    temperature=0.2,
)

# ---------------- Utilities ----------------
def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

def _geocode(place: str):
    geolocator = Nominatim(user_agent="swarm-aid")
    loc = geolocator.geocode(place)
    if not loc:
        return None
    return (loc.latitude, loc.longitude)

def _fetch_eonet_events():
    # Open events; raise the limit a bit so we have options
    url = "https://eonet.gsfc.nasa.gov/api/v3/events"
    params = {"status": "open", "limit": 100}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("events", [])

def eonet_hazard_scan(query: str) -> str:
    """
    Geocode the scenario location, pull current EONET hazards,
    filter to those within ~500km, and summarize implications.
    """
    # 1) Geocode
    loc = _geocode(query)
    if not loc:
        return f"Could not geocode location from: {query}. Provide a clearer place name."

    lat, lon = loc

    # 2) Fetch hazards
    try:
        events = _fetch_eonet_events()
    except Exception as e:
        # non-blocking fallback
        demo = [
            {"title": "Severe Storms (demo)", "category": "Severe Storms", "distance_km": 25, "when": "now"},
            {"title": "Flood Event (demo)", "category": "Floods", "distance_km": 120, "when": "12h"},
        ]
        demo_text = "\n".join(f"- {d['title']} · {d['category']} · ~{d['distance_km']} km · {d['when']}" for d in demo)
        summary = llm.invoke(
            f"(EONET unavailable) Location=({lat:.4f},{lon:.4f}). "
            f"Given these demo hazards, analyze likely damage zones and vulnerable districts:\n{demo_text}"
        )
        return summary.content

    # 3) Distance filter + compact list
    nearby = []
    for ev in events:
        cats = [c.get("title", "") for c in ev.get("categories", [])]
        geoms = ev.get("geometry", [])
        if not geoms:
            continue
        # Use most recent geometry entry
        g = geoms[-1]
        coords = g.get("coordinates")
        if not coords or not isinstance(coords, (list, tuple)) or len(coords) < 2:
            continue
        # EONET stores [lon, lat]
        try:
            ev_lon, ev_lat = float(coords[0]), float(coords[1])
        except Exception:
            continue
        d_km = _haversine(lat, lon, ev_lat, ev_lon)
        if d_km <= 1000:  # within 500 km of scenario
            nearby.append({
                "title": ev.get("title", "Event"),
                "category": ", ".join(cats) if cats else "Uncategorized",
                "distance_km": round(d_km),
                "when": g.get("date", ""),
            })

    if not nearby:
        return (
            "No active EONET hazards within ~1000 km of the scenario. "
            "Proceed with local reports, social signals, and civil defense bulletins."
        )

    # 4) Summarize with LLM
    nearby_sorted = sorted(nearby, key=lambda x: x["distance_km"])[:10]
    bullet = "\n".join(
        f"- {n['title']} · {n['category']} · ~{n['distance_km']} km · {n['when']}"
        for n in nearby_sorted
    )
    prompt = (
        f"Scenario location: ({lat:.4f}, {lon:.4f}). Recent nearby hazards:\n{bullet}\n\n"
        "Based on these events, write a concise analysis of likely damage zones, infrastructure risks, "
        "and which districts need the fastest assessment. Be practical and location-aware."
    )
    summary = llm.invoke(prompt)
    return summary.content

tools = [
    Tool(
        name="EONET Hazard Scan",
        func=eonet_hazard_scan,
        description="Scan NASA EONET for active natural hazards near a place and summarize implications."
    )
]

data_analyst = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True,
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
