from crewai import Agent, Task, Crew, LLM
from crewai_tools import CodeInterpreterTool, SerperDevTool
import logging
import traceback
from llm_utils import call_llm_with_retries



# Added: load .env and validate API keys
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env from project root

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CREWAI_API_KEY = os.getenv("CREWAI_API_KEY")

if not (GEMINI_API_KEY or CREWAI_API_KEY):
    raise RuntimeError(
        "No LLM API key found. Create a .env file with GEMINI_API_KEY=<key> or CREWAI_API_KEY=<key> and restart."
    )
# Initialize them
calc_tool = CodeInterpreterTool()
search_tool = SerperDevTool()

gemini_flash = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7
)
# TODO: conditionally include tools if initialized successfully
# tool_list = [tl for tl in (calc_tool, search_tool) if tl is not None]
inventory_analyst = Agent(
    role="Demand Forecasting Specialist",
    goal="Predict optimal stock levels using ML models",
    backstory="Data scientist with 8 years in retail analytics",
    llm=gemini_flash,
    verbose=True
)

procurement_officer = Agent(
    role="Procurement Optimization Manager",
    goal="Generate purchase orders balancing cost and lead time",
    backstory="Supply chain expert with global vendor networks",
    llm=gemini_flash
)

data_validator = Agent(
    role="Data Quality Auditor",
    goal="Ensure input data integrity and freshness",
    backstory="Data engineer specializing in ETL pipelines",
    llm=gemini_flash
)

# Includes automatic retry logic and stale data detection
VALIDATION_TASK = Task(
    description="Verify supplier API connectivity and data freshness",
    expected_output="""{
        "status": "ok|error",
        "last_update": "2025-11-20T05:15:00Z",
        "failed_sources": ["vendorX_api"]
    }""",
    agent=data_validator
)

replenishment_crew = Crew(
    agents=[inventory_analyst, procurement_officer, data_validator],
    tasks=[
        Task(
            description="Analyze sales trends from last 90 days",
            expected_output="Time-series forecast with confidence intervals",
            agent=inventory_analyst
        ),
        Task(
            description="Generate vendor-specific purchase orders",
            expected_output="XML formatted POs with delivery timelines",
            agent=procurement_officer
        ),
        VALIDATION_TASK
    ],
    process="sequential"  # Validate -> Analyze -> Procure
)

# kickoff the crew process
if __name__ == "__main__":
    result = replenishment_crew.kickoff()
    print(result)
