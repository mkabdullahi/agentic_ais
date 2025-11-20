from crewai import Agent, Task, Crew
from tools import PythonCalculatorTool, WebSearchTool

# Added: load .env and validate API keys
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env from project root

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CREWAI_API_KEY = os.getenv("CREWAI_API_KEY")

if not (OPENAI_API_KEY or CREWAI_API_KEY):
    raise RuntimeError(
        "No LLM API key found. Create a .env file with OPENAI_API_KEY=<key> or CREWAI_API_KEY=<key> and restart."
    )
clinical_coordinator = Agent(
    role="Clinical Research Coordinator",
    goal="Identify eligible patients and coordinate trial enrollment",
    backstory="CRC with experience in oncology trial workflows",
    llm="gpt-4o-mini",
    tools=[WebSearchTool],
    verbose=True
)

trial_data_engineer = Agent(
    role="Trial Registry Data Engineer",
    goal="Aggregate and normalize trial metadata from registries",
    backstory="Data engineer focused on clinical data pipelines",
    llm="gpt-4o-mini",
    tools=[PythonCalculatorTool]
)

patient_screening_agent = Agent(
    role="Patient Screening Specialist",
    goal="Screen EHR data for eligibility criteria",
    backstory="Clinical informaticist skilled at EHR-derived phenotyping",
    llm="gpt-4o-mini"
)

VALIDATION_TASK = Task(
    description="Verify clinical registry API access and timestamp freshness",
    expected_output="""{
        "status": "ok|error",
        "last_sync": "2025-11-20T05:15:00Z",
        "missing_registries": ["euctr"]
    }""",
    agent=trial_data_engineer
)

matching_crew = Crew(
    agents=[trial_data_engineer, patient_screening_agent, clinical_coordinator],
    tasks=[
        VALIDATION_TASK,
        Task(
            description="Normalize trial inclusion/exclusion criteria from registries",
            expected_output="Structured criteria usable for programmatic matching",
            agent=trial_data_engineer
        ),
        Task(
            description="Screen patient EHR records for candidate matches",
            expected_output="Ranked list of candidate patients with match scores",
            agent=patient_screening_agent
        ),
        Task(
            description="Generate referral summaries and enrollment instructions",
            expected_output="Patient-facing referral package and site contact info",
            agent=clinical_coordinator
        )
    ],
    process="sequential"  # Validate -> Normalize -> Screen -> Refer
)

# kickoff the crew process
result = matching_crew.kickoff()
display(result)