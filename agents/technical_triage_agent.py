from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, CodeInterpreterTool

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

oncall_engineer = Agent(
    role="On-call Site Reliability Engineer",
    goal="Diagnose production outages and recommend remediation steps",
    backstory="SRE with 6 years handling distributed system incidents",
    llm=gemini_flash,
    tools=[calc_tool, search_tool],
    verbose=True
)

diagnostics_agent = Agent(
    role="Automated Diagnostics Agent",
    goal="Run health checks, collect logs and surface root-cause signals",
    backstory="Observability specialist embedded into monitoring stack",
    llm=gemini_flash
)

escalation_manager = Agent(
    role="Incident Escalation Coordinator",
    goal="Decide when to escalate and prepare communications",
    backstory="Incident manager with experience coordinating cross-team response",
    llm=gemini_flash
)

VALIDATION_TASK = Task(
    description="Verify monitoring and alerting webhook connectivity",
    expected_output="""{
        "status": "ok|error",
        "last_checked": "2025-11-20T05:15:00Z",
        "failed_endpoints": ["pagerduty_webhook"]
    }""",
    agent=diagnostics_agent
)

triage_crew = Crew(
    agents=[diagnostics_agent, oncall_engineer, escalation_manager],
    tasks=[
        VALIDATION_TASK,
        Task(
            description="Run automated diagnostics across services flagged by alerts",
            expected_output="List of failing services, error traces, and likely root causes",
            agent=diagnostics_agent
        ),
        Task(
            description="Produce incident remediation steps and escalation notes",
            expected_output="Step-by-step playbook + teams to notify",
            agent=oncall_engineer
        ),
        Task(
            description="Prepare stakeholder communication and decide escalation",
            expected_output="Incident severity, timeline, and escalation decision",
            agent=escalation_manager
        )
    ],
    process="sequential"  # Validate -> Diagnose -> Remediate -> Escalate
)

# kickoff the crew process
if __name__ == "__main__":
    result = triage_crew.kickoff()
    print(result)