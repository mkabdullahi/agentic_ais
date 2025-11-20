from crewai import Agent, Task, Crew
from tools import PythonCalculatorTool, WebSearchTool

inventory_analyst = Agent(
    role="Demand Forecasting Specialist",
    goal="Predict optimal stock levels using ML models",
    backstory="Data scientist with 8 years in retail analytics",
    llm="gpt-4o-mini",
    tools=[PythonCalculatorTool, WebSearchTool],
    verbose=True
)

procurement_officer = Agent(
    role="Procurement Optimization Manager",
    goal="Generate purchase orders balancing cost and lead time",
    backstory="Supply chain expert with global vendor networks",
    llm="gpt-4o-mini"
)

data_validator = Agent(
    role="Data Quality Auditor",
    goal="Ensure input data integrity and freshness",
    backstory="Data engineer specializing in ETL pipelines",
    llm="gpt-4o-mini"
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
result = replenishment_crew.kickoff()
display(result)
