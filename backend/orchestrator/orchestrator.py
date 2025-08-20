from agents.data_analyst import data_analyst
from agents.medic_coordinator import medic_coordinator
from agents.logistics_manager import logistics_manager
from agents.critic import critic
from geopy.geocoders import Nominatim
import random

def generate_geojson(scenario: str):
    geolocator = Nominatim(user_agent="swarm-aid")
    location = geolocator.geocode(scenario)

    if not location:
        return {"type": "FeatureCollection", "features": []}

    lat, lon = location.latitude, location.longitude

    # Example: generate random demo damage zones & routes near location
    features = []

    # Damage Zone
    features.append({
        "type": "Feature",
        "properties": {"name": "Damage Zone A", "severity": "severe"},
        "geometry": {"type": "Point", "coordinates": [lon, lat]}
    })

    # Another Damage Zone slightly offset
    features.append({
        "type": "Feature",
        "properties": {"name": "Damage Zone B", "severity": "moderate"},
        "geometry": {"type": "Point", "coordinates": [lon + 0.05, lat + 0.05]}
    })

    # Safe Route (simple line)
    features.append({
        "type": "Feature",
        "properties": {"name": "Safe Route 1", "type": "safe_route"},
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [lon - 0.1, lat - 0.1],
                [lon, lat],
                [lon + 0.1, lat + 0.1],
            ]
        }
    })

    return {"type": "FeatureCollection", "features": features}


def run_simulation(scenario: str):
    """
    Orchestrates the 4 agents to analyze a crisis scenario step by step,
    and produces both logs + demo GeoJSON.
    """

    logs = []

    # 1. Data Analyst
    try:
        analysis = data_analyst.run(f"Analyze damage zones for: {scenario}")
        logs.append({"agent": "Data Analyst", "response": analysis})
    except Exception as e:
        analysis = f"⚠️ Error: {e}"
        logs.append({"agent": "Data Analyst", "response": analysis})

    # 2. Medic Coordinator
    try:
        triage = medic_coordinator.run(f"Prioritize medical needs based on {analysis}")
        logs.append({"agent": "Medic Coordinator", "response": triage})
    except Exception as e:
        triage = f"⚠️ Error: {e}"
        logs.append({"agent": "Medic Coordinator", "response": triage})

    # 3. Logistics Manager
    try:
        routes = logistics_manager.run(f"Plan safe supply routes based on {analysis} and {triage}")
        logs.append({"agent": "Logistics Manager", "response": routes})
    except Exception as e:
        routes = f"⚠️ Error: {e}"
        logs.append({"agent": "Logistics Manager", "response": routes})

    # 4. Critic Agent
    try:
        critique = critic.run(f"Audit this plan: Analysis={analysis}, Triage={triage}, Routes={routes}")
        logs.append({"agent": "Critic", "response": critique})
    except Exception as e:
        logs.append({"agent": "Critic", "response": f"⚠️ Error: {e}"})

    geojson = generate_geojson(scenario)

    return {"scenario": scenario, "logs": logs, "geojson": geojson}
