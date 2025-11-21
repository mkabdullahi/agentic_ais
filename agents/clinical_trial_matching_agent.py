from crewai import Agent, Task, Crew, LLM
from crewai_tools import CodeInterpreterTool, SerperDevTool

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
web_search_tool = SerperDevTool()
python_calculator_tool = CodeInterpreterTool()

gemini_flash = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7
)

# TODO: conditionally include tools if initialized successfully
# tool_list = [tl for tl in (calc_tool, search_tool) if tl is not None]

clinical_coordinator = Agent(
    role="Clinical Research Coordinator",
    goal="Identify eligible patients and coordinate trial enrollment",
    backstory="CRC with experience in oncology trial workflows",
    llm=gemini_flash,
    verbose=True
)

# TODO: conditionally include tools if initialized successfully
# tool_list = [tl for tl in (calc_tool, search_tool) if tl is not None]

trial_data_engineer = Agent(
    role="Trial Registry Data Engineer",
    goal="Aggregate and normalize trial metadata from registries",
    backstory="Data engineer focused on clinical data pipelines",
    llm=gemini_flash
)

patient_screening_agent = Agent(
    role="Patient Screening Specialist",
    goal="Screen EHR data for eligibility criteria",
    backstory="Clinical informaticist skilled at EHR-derived phenotyping",
    llm=gemini_flash
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
if __name__ == "__main__":
    result = matching_crew.kickoff()
    print(result)