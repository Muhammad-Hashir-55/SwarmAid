# orchestrator/orchestrator.py
from agents.data_analyst import data_analyst
from agents.medic_coordinator import medic_coordinator
from agents.logistics_manager import logistics_manager, compute_route_features
from agents.critic import critic
from geopy.geocoders import Nominatim


def generate_geojson(scenario: str):
    """
    Generate crisis GeoJSON features:
      - Damage zones (random demo points)
      - Routes & staging nodes from Logistics Manager
    """
    geolocator = Nominatim(user_agent="swarm-aid")
    location = None
    try:
        location = geolocator.geocode(scenario, timeout=5)
    except Exception:
        pass

    if not location:
        return {"type": "FeatureCollection", "features": []}

    lat, lon = location.latitude, location.longitude
    features = []

    # Example Damage Zone A
    features.append({
        "type": "Feature",
        "properties": {
            "name": "Damage Zone A",
            "severity": "severe",
            "type": "damage"   # ✅ tag for frontend
        },
        "geometry": {"type": "Point", "coordinates": [lon, lat]}
    })

    # Example Damage Zone B (slightly offset)
    features.append({
        "type": "Feature",
        "properties": {
            "name": "Damage Zone B",
            "severity": "moderate",
            "type": "damage"   # ✅ tag for frontend
        },
        "geometry": {"type": "Point", "coordinates": [lon + 0.05, lat + 0.05]}
    })

    # ✅ Add Logistics Manager route features
    try:
        route_pack = compute_route_features(scenario)
        for f in route_pack["features"]:
            if "properties" not in f:
                f["properties"] = {}
            f["properties"]["type"] = "route"   # ✅ tag all logistics routes
        features.extend(route_pack["features"])
    except Exception as e:
        print(f"⚠️ Logistics route generation failed: {e}")
        # If routing fails, continue with damage zones only

    return {"type": "FeatureCollection", "features": features}


def run_simulation(scenario: str):
    """
    Orchestrates the 4 agents to analyze a crisis scenario step by step,
    and produces both logs + GeoJSON.
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
        # 🔹 If in future we add geo features for triage, set `type: triage`
    except Exception as e:
        triage = f"⚠️ Error: {e}"
        logs.append({"agent": "Medic Coordinator", "response": triage})

    # 3. Logistics Manager
    try:
        # Get both the textual plan (via agent) and GeoJSON features (via compute_route_features)
        routes_text = logistics_manager.run(f"Plan safe supply routes based on {analysis} and {triage}")
        route_pack = compute_route_features(scenario)
        logs.append({"agent": "Logistics Manager", "response": routes_text})
        if route_pack.get("summary"):
            logs.append({"agent": "Logistics Manager (GeoJSON)", "response": route_pack["summary"]})
    except Exception as e:
        routes_text = f"⚠️ Error: {e}"
        logs.append({"agent": "Logistics Manager", "response": routes_text})

    # 4. Critic Agent
    try:
        critique = critic.run(f"Audit this plan: Analysis={analysis}, Triage={triage}, Routes={routes_text}")
        logs.append({"agent": "Critic", "response": critique})
    except Exception as e:
        logs.append({"agent": "Critic", "response": f"⚠️ Error: {e}"})

    # ✅ Build final GeoJSON
    geojson = generate_geojson(scenario)

    return {"scenario": scenario, "logs": logs, "geojson": geojson}
