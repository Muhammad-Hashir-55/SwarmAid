from crewai import Agent
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    model="gpt-5", 
    api_key=os.getenv("OPENAI_API_KEY"), 
    base_url="https://api.aimlapi.com/v1", 
    temperature=0.2
)

data_analyst = Agent(
    role="Senior Geospatial Analyst",
    goal="Identify disaster impact zones using satellite data",
    backstory="Expert in remote sensing and disaster assessment",
    tools=[],
    llm=llm,
    verbose=True
)
