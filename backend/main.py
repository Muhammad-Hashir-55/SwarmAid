from fastapi import FastAPI
from agents.data_analyst import data_analyst

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Backend running 🚀"}

@app.get("/analyze")
def analyze_disaster():
    response = data_analyst.think("Analyze damage in Tokyo earthquake")
    return {"analysis": response}
#salaar