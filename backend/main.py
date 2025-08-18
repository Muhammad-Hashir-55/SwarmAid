from fastapi import FastAPI
from orchestrator.orchestrator import run_simulation

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Backend running 🚀"}

@app.get("/simulate")
def simulate_crisis(scenario: str = "Tokyo earthquake"):
    result = run_simulation(scenario)
    return result
