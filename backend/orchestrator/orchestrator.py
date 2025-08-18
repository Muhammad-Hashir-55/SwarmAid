from agents.data_analyst import data_analyst
from agents.medic_coordinator import medic_coordinator
from agents.logistics_manager import logistics_manager
from agents.critic import critic

def run_simulation(scenario: str):
    """
    Orchestrates the 4 agents to analyze a crisis scenario step by step.
    """

    logs = []

    # 1. Data Analyst
    try:
        analysis = data_analyst.run(f"Analyze damage zones for: {scenario}")
        logs.append({"agent": "Data Analyst", "response": analysis})
    except Exception as e:
        logs.append({"agent": "Data Analyst", "response": f"⚠️ Error: {e}"})

    # 2. Medic Coordinator
    try:
        triage = medic_coordinator.run(f"Prioritize medical needs based on {analysis}")
        logs.append({"agent": "Medic Coordinator", "response": triage})
    except Exception as e:
        logs.append({"agent": "Medic Coordinator", "response": f"⚠️ Error: {e}"})

    # 3. Logistics Manager
    try:
        routes = logistics_manager.run(f"Plan safe supply routes based on {analysis} and {triage}")
        logs.append({"agent": "Logistics Manager", "response": routes})
    except Exception as e:
        logs.append({"agent": "Logistics Manager", "response": f"⚠️ Error: {e}"})

    # 4. Critic Agent
    try:
        critique = critic.run(f"Audit this plan: Analysis={analysis}, Triage={triage}, Routes={routes}")
        logs.append({"agent": "Critic", "response": critique})
    except Exception as e:
        logs.append({"agent": "Critic", "response": f"⚠️ Error: {e}"})

    return {"scenario": scenario, "logs": logs}
