# agents/logistics_manager.py
from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
from geopy.geocoders import Nominatim
import requests
from .keys import ss, ORS_API_KEY  # ORS_API_KEY should be in keys.py

# ----------------- Setup LLM -----------------
AIML_API_KEY = ss
llm = ChatOpenAI(
    model="gpt-5-chat-latest",
    api_key=AIML_API_KEY,
    base_url="https://api.aimlapi.com/v1",
    temperature=0.2
)

# ----------------- Utility Functions -----------------
def _geocode(place: str):
    """Convert place name into (lat, lon)."""
    geolocator = Nominatim(user_agent="swarm-aid")
    loc = geolocator.geocode(place)
    return (loc.latitude, loc.longitude) if loc else None


def _route_osrm(start_lat, start_lon, end_lat, end_lon):
    """Fallback: Open Source Routing Machine (OSRM)."""
    url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
    params = {"overview": "false", "alternatives": "false", "geometries": "geojson"}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    js = r.json()
    if not js.get("routes"):
        raise ValueError("No OSRM route found")
    r0 = js["routes"][0]
    return {
        "engine": "osrm",
        "distance_km": round(r0["distance"] / 1000, 1),
        "duration_min": round(r0["duration"] / 60, 1),
        "geojson": r0.get("geometry")
    }


def _route_ors(start_lat, start_lon, end_lat, end_lon, api_key: str):
    """Preferred: OpenRouteService (ORS) with your API key."""
    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    print(f"📡 ORS request URL: {url}")  # Debugging line
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    payload = {
        "coordinates": [[start_lon, start_lat], [end_lon, end_lat]]
    }
    r = requests.post(url, headers=headers, json=payload, timeout=25)
    r.raise_for_status()
    js = r.json()
    feat = js["features"][0]
    summ = feat["properties"]["summary"]
    return {
        "engine": "openrouteservice",
        "distance_km": round(summ["distance"] / 1000, 1),
        "duration_min": round(summ["duration"] / 60, 1),
        "geojson": feat.get("geometry")
    }


# ----------------- Core Tool -----------------
def plan_safe_routes(query: str) -> str:
    """
    Geocode the location, generate a staging → hospital route,
    try OpenRouteService first (if key valid), else OSRM fallback.
    Returns a logistics-focused summary.
    """
    loc = _geocode(query)
    if not loc:
        return f"❌ Could not geocode location from: {query}. Try a clearer place name."

    lat, lon = loc
    start = (lat - 0.15, lon - 0.15)  # staging base
    end   = (lat + 0.10, lon + 0.10)  # field hospital

    # Pick ORS if possible, else fallback to OSRM
    try:
        if ORS_API_KEY:
            try:
                route = _route_ors(start[0], start[1], end[0], end[1], ORS_API_KEY)
            except Exception as ors_error:
                print(f"⚠️ ORS failed: {ors_error}, falling back to OSRM...")
                route = _route_osrm(start[0], start[1], end[0], end[1])
        else:
            route = _route_osrm(start[0], start[1], end[0], end[1])
    except Exception as e:
        return (
            f"⚠️ Routing failed ({e}). Use ring roads and secondary arterials from "
            f"{start} toward {end}. Place refuel and comms nodes every 8–12 km."
        )

    # Let LLM generate human-friendly logistics plan
    prompt = (
        f"Plan safe supply routes for '{query}'. "
        f"Primary corridor ({route['engine']}): ~{route['distance_km']} km, "
        f"~{route['duration_min']} min, staging at {start}, destination at {end}. "
        "Give step-by-step logistics guidance: entry corridors, alternates, "
        "staging depots, ambulance lanes, and avoid bridges/overpasses."
    )
    return llm.invoke(prompt).content


# ----------------- Tools & Agent -----------------
tools = [
    Tool(
        name="Route Planner",
        func=plan_safe_routes,
        description=(
            "Use this to compute real road routes between staging and a field hospital "
            "for a given location. It outputs a logistics summary with distances, "
            "timing, staging depots, and alternate corridors."
        ),
    )
]

logistics_manager = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True
)

# # ✅ Ready to import in main app or test with:
# response = logistics_manager.run("Plan a safe route near Lahore")
# print(response)


# # --- Optional interactive loop ---
# print("🚚 Chat with Logistics Manager Agent (type 'exit' to quit)\n")
# print("Role: Logistics Manager")
# print("Goal: Plan safe and efficient supply routes\n")

# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("👋 Exiting...")
#         break

#     try:
#         response = logistics_manager.run(user_input)
#         print(f"\nLogistics Manager: {response}\n")
#     except Exception as e:
#         print(f"\n⚠️ Parsing issue, showing raw LLM response:\n{str(e)}\n")
#         try:
#             raw_response = llm.invoke(user_input)
#             print(f"Logistics Manager (raw): {raw_response.content}\n")
#         except Exception as inner_e:
#             print(f"❌ Fallback also failed: {inner_e}\n")
#     except Exception as e:
#         print(f"⚠️ Unexpected error: {e}\n")
