from llama_index.core.agent.workflow import (
    AgentWorkflow,
    FunctionAgent,
)

# custom modules
from neosearch.settings import Settings
from neosearch.engine.prompts.deep_research import (
    RESEARCH_AGENT_SYSTEM_PROMPT,
    RESEARCH_WRITE_AGENT_SYSTEM_PROMPT,
    RESEARCH_REVIEW_AGENT_SYSTEM_PROMPT,
)

from .tools import (
    search_web,
    record_notes,
    write_report,
    review_report,
)

def _get_research_agent(llm) -> FunctionAgent:
    return FunctionAgent(
        name="ResearchAgent",
        description="Useful for searching the web for information on a given topic and recording notes on the topic.",
        system_prompt=str(RESEARCH_AGENT_SYSTEM_PROMPT),
        llm=llm,
        tools=[search_web, record_notes],
        can_handoff_to=["WriteAgent"],
    )


def _get_write_agent(llm) -> FunctionAgent:
    return FunctionAgent(
        name="WriteAgent",
        description="Useful for writing a report on a given topic.",
        system_prompt=str(RESEARCH_WRITE_AGENT_SYSTEM_PROMPT),
        llm=llm,
        tools=[write_report],
        can_handoff_to=["ReviewAgent", "ResearchAgent"],
    )


def _get_review_agent(llm) -> FunctionAgent:
    return FunctionAgent(
        name="ReviewAgent",
        description="Useful for reviewing a report and providing feedback.",
        system_prompt=str(RESEARCH_REVIEW_AGENT_SYSTEM_PROMPT),
        llm=llm,
        tools=[review_report],
        can_handoff_to=["WriteAgent"],
    )


def get_sub_agents_for_research() -> tuple[FunctionAgent, FunctionAgent, FunctionAgent]:
    llm = Settings.llm

    research_agent = _get_research_agent(llm)
    write_agent = _get_write_agent(llm)
    review_agent = _get_review_agent(llm)

    return (
        research_agent, write_agent, review_agent
    )


def get_research_workflow_agent() -> AgentWorkflow:
    (
        research_agent, write_agent, review_agent
    ) = get_sub_agents_for_research()

    agent_workflow = AgentWorkflow(
        agents=[research_agent, write_agent, review_agent],
        root_agent=research_agent.name,
        initial_state={
            "research_notes": {},
            "report_content": "Not written yet.",
            "review": "Review required.",
        },
    )

    return agent_workflow
