# agents/logistics_manager.py
from __future__ import annotations

from functools import lru_cache
from time import sleep
from typing import Dict, Any, List, Tuple, Optional

import requests
from requests.exceptions import RequestException, Timeout

from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

from .keys import ss, ORS_API_KEY  # ORS_API_KEY must exist in keys.py (string or "")

# ----------------- Setup LLM -----------------
AIML_API_KEY = ss
llm = ChatOpenAI(
    model="gpt-5-chat-latest",
    api_key=AIML_API_KEY,
    base_url="https://api.aimlapi.com/v1",
    temperature=0.2,
)

# ----------------- Geocoding -----------------
@lru_cache(maxsize=256)
def _geocode(place: str) -> Optional[Tuple[float, float]]:
    """
    Convert place name into (lat, lon) with sane timeouts and retry.
    Nominatim requires a descriptive user_agent.
    """
    geo = Nominatim(user_agent="swarm-aid-logistics/1.0 (contact: ops@swarm-aid.local)", timeout=5)
    # Try up to 3 attempts (handles transient timeouts)
    for attempt in range(3):
        try:
            loc = geo.geocode(place, addressdetails=False, exactly_one=True)
            if loc:
                return (loc.latitude, loc.longitude)
            return None
        except (GeocoderUnavailable, GeocoderTimedOut):
            sleep(0.6)  # small backoff
        except Exception:
            break
    return None


# ----------------- Routing Engines -----------------
def _route_osrm(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> Dict[str, Any]:
    """
    Public OSRM fallback (no key required).
    """
    url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
    params = {"overview": "full", "alternatives": "false", "geometries": "geojson"}
    try:
        r = requests.get(url, params=params, timeout=25)
        r.raise_for_status()
        js = r.json()
        if not js.get("routes"):
            raise ValueError("No OSRM route found")
        r0 = js["routes"][0]
        geom = r0.get("geometry")
        return {
            "engine": "osrm",
            "distance_km": round(r0["distance"] / 1000.0, 1),
            "duration_min": round(r0["duration"] / 60.0, 1),
            "geometry": geom,  # GeoJSON LineString
        }
    except (RequestException, Timeout) as e:
        raise RuntimeError(f"OSRM routing failed: {e}")


def _route_ors(start_lat: float, start_lon: float, end_lat: float, end_lon: float, api_key: str) -> Dict[str, Any]:
    """
    OpenRouteService (preferred). Requires ORS_API_KEY.
    """
    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    payload = {"coordinates": [[start_lon, start_lat], [end_lon, end_lat]]}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        js = r.json()
        feat = js["features"][0]
        summ = feat["properties"]["summary"]
        return {
            "engine": "openrouteservice",
            "distance_km": round(summ["distance"] / 1000.0, 1),
            "duration_min": round(summ["duration"] / 60.0, 1),
            "geometry": feat.get("geometry"),  # GeoJSON LineString
        }
    except (RequestException, Timeout) as e:
        raise RuntimeError(f"ORS routing failed: {e}")


# ----------------- Public Helpers (used by orchestrator) -----------------
def compute_route_features(query: str) -> Dict[str, Any]:
    """
    Returns a dict with:
      - 'summary': text (LLM plan)
      - 'features': [GeoJSON Feature, ...] for route + markers
    """
    loc = _geocode(query)
    if not loc:
        # Provide a graceful summary + no features
        return {
            "summary": (
                f"❌ Could not geocode a precise point for: '{query}'. "
                "Please try a more specific place (e.g., 'Lahore, Pakistan' instead of 'America')."
            ),
            "features": [],
        }

    lat, lon = loc

    # Create a simple scenario: staging base to field hospital, offset from center.
    start = (lat - 0.15, lon - 0.15)
    end = (lat + 0.10, lon + 0.10)

    # Try ORS, then OSRM
    try:
        if ORS_API_KEY and len(ORS_API_KEY.strip()) > 0:
            try:
                route = _route_ors(start[0], start[1], end[0], end[1], ORS_API_KEY)
            except Exception as ors_err:
                # Fallback transparently to OSRM
                route = _route_osrm(start[0], start[1], end[0], end[1])
        else:
            route = _route_osrm(start[0], start[1], end[0], end[1])
    except Exception as e:
        # Return a text fallback + empty features
        return {
            "summary": (
                f"⚠️ Routing temporarily unavailable ({e}). "
                f"Interim guidance: move via secondary arterials from {start} toward {end}, "
                "avoid bridge choke-points, set refuel/relay every 8–12 km."
            ),
            "features": [],
        }

    # Build features for the frontend map
    line_feature = {
        "type": "Feature",
        "geometry": route["geometry"],  # already a GeoJSON LineString
        "properties": {
            "name": f"Primary Corridor ({route['engine']})",
            "severity": "route",
            "distance_km": route["distance_km"],
            "duration_min": route["duration_min"],
        },
    }

    start_feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [start[1], start[0]]},
        "properties": {"name": "Staging Base", "severity": "moderate"},
    }

    end_feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [end[1], end[0]]},
        "properties": {"name": "Field Hospital", "severity": "severe"},
    }

    # Human-friendly logistics plan (LLM)
    prompt = (
        f"Plan safe supply routes for '{query}'. "
        f"Primary corridor via {route['engine']}: ~{route['distance_km']} km, "
        f"~{route['duration_min']} min. "
        f"Staging at {start}, destination at {end}. "
        "Give step-by-step logistics guidance: entry corridors, alternates, "
        "staging depots, ambulance lanes, bridge/overpass avoidance, and refuel/comms nodes."
    )
    plan_text = llm.invoke(prompt).content

    return {
        "summary": plan_text,
        "features": [line_feature, start_feature, end_feature],
    }


# ----------------- LangChain Tool (string-only, for chat) -----------------
def plan_safe_routes_tool(query: str) -> str:
    """
    Tool wrapper: returns only the textual plan for the agent chat.
    """
    result = compute_route_features(query)
    return result["summary"]


# ----------------- Tools & Agent -----------------
tools = [
    Tool(
        name="Route Planner",
        func=plan_safe_routes_tool,
        description=(
            "Compute real road routes (staging → field hospital) for a given location. "
            "Outputs a logistics summary with distances, timing, staging depots, and alternates."
        ),
    )
]

logistics_manager = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True,
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
