from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.orchestrator import run_simulation

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend running 🚀"}

@app.get("/simulate")
def simulate_crisis(scenario: str = "Tokyo earthquake"):
    result = run_simulation(scenario)
    return result
