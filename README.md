# CrewAI Agents — README

This repository contains examples of multi-agent "crew" workflows built with the CrewAI primitives: Agent, Task, and Crew. Each example demonstrates a small, focused automation that composes multiple agents (LLMs + tools) to perform a domain workflow end-to-end.

## Contents

- agents/
  - inventory_optimization_agent.py — demand forecasting, data validation, procurement PO generation
  - technical_triage_agent.py — monitoring validation, diagnostics, incident remediation & escalation
  - clinical_trial_matching_agent.py — trial registry normalization, EHR screening, referral generation
- README.md — this document

## Goals

- Provide clear, reusable examples of how to structure agents, validation tasks, and sequential crew processes.
- Show usage patterns for attaching tools to agents and for running crews end-to-end.
- Serve as a starter template for building production crews (validation → task pipeline → handoff/communication).

## Agent patterns

Each example follows a similar structure:

- Define Agent instances with:
  - role: human-friendly description of the agent's role
  - goal: short objective for the agent
  - backstory: optional persona context for better responses
  - llm: model identifier used by the Agent
  - tools: list of tool classes (optional)
  - verbose: boolean to output agent traces (optional)
- Define Task instances:
  - description: what to do
  - expected_output: schema or natural-language expectation for the task result
  - agent: which Agent executes the task
- Compose a Crew:
  - agents: list of involved Agent instances
  - tasks: ordered list of Task instances (can include validation tasks)
  - process: "sequential" (current examples) — may be extended to other orchestration styles
- Kick off with crew.kickoff() and inspect/display the result.

## Example summaries

1. Inventory optimization
   - Agents: Demand Forecasting Specialist, Procurement Optimization Manager, Data Quality Auditor
   - Key tasks: data validation (supplier APIs), sales trend forecasting (90d), vendor-specific PO generation (XML)
   - Tools: PythonCalculatorTool, WebSearchTool (attached to forecasting agent)

2. Technical triage
   - Agents: Automated Diagnostics Agent, On-call SRE, Incident Escalation Coordinator
   - Key tasks: monitoring/webhook validation, run diagnostics across services, produce remediation playbook, prepare stakeholder communications
   - Tools: PythonCalculatorTool, WebSearchTool (attached to on-call SRE)

3. Clinical trial matching
   - Agents: Trial Registry Data Engineer, Patient Screening Specialist, Clinical Research Coordinator
   - Key tasks: registry API validation, normalize inclusion/exclusion criteria, screen EHR records, generate referral packages
   - Tools: PythonCalculatorTool, WebSearchTool (attached selectively)

## How to run locally (Mac)

1. Create and activate a virtual environment
   - python3 -m venv .venv
   - source .venv/bin/activate

2. Install dependencies (example)
   - pip install -r requirements.txt
   - If you don't have requirements.txt, install your LLM client and supporting libs, e.g.:
     - pip install crewai openai

3. Run an example
   - python agents/inventory_optimization_agent.py
   - python agents/technical_triage_agent.py
   - python agents/clinical_trial_matching_agent.py

4. Inspect output
   - Scripts call display(result). In a terminal script run, result is returned by kickoff(); printing or logging result is recommended:
     - python -c "from agents.inventory_optimization_agent import replenishment_crew; print(replenishment_crew.kickoff())"

## Configuration

- LLM selection: change the llm argument on Agent creation (examples use "gpt-4o-mini").
- Tools: attach tool classes to agents via the tools parameter. Tools must be implemented in the repository (see tools.py).
- Verbose traces: set verbose=True on agents to surface intermediate reasoning and tool calls.

## Expected outputs & validation schemas

Each Task includes an expected_output field describing the desired format or schema (JSON snippet or natural language). Use these schemas to:
- Validate agent responses programmatically.
- Implement automated retries and stale-data detection in a validation agent.

## Extending the examples

- Add parallel processes: implement Crew with process="parallel" or a custom orchestrator.
- Add retries and error handling: expand the validation agent to return structured failure codes and remediation hints.
- Add unit tests: create tests that mock LLM responses and tool outputs to validate orchestration logic.

## Troubleshooting

- If kickoff() hangs: enable verbose on agents to see tool calls and responses.
- Missing tool import errors: ensure tools.py is in PYTHONPATH and the tool class names match.
- API/auth errors: ensure environment variables for LLM and external services are set (export OPENAI_API_KEY=...).

## Testing suggestions

- Unit test each Agent by mocking LLM responses.
- Unit test Crew orchestration with mocked agent.execute/task output.
- Use pytest and pytest-mock for isolation.

## Security & privacy notes

- Clinical example touches on protected health data (EHR). Do not run with real PHI unless your environment complies with applicable regulations (e.g., HIPAA).
- Mask or redact sensitive data passed to external LLMs or third-party tools.

## License

Add your preferred license file (LICENSE) to the repo.

## Contact / Next steps

- Use these files as templates to implement production-grade crews:
  - improve validation robustness
  - add observability and logging
  - add retry/backoff for flaky external APIs
  - integrate with orchestration systems (Airflow, temporal, etc.)
