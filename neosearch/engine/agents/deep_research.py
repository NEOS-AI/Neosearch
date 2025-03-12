from tavily import AsyncTavilyClient
from llama_index.core.agent.workflow import (
    AgentWorkflow,
    FunctionAgent,
    AgentInput,
    AgentOutput,
    ToolCall,
    ToolCallResult,
    AgentStream,
)

from llama_index.core.workflow import Context
import os
import asyncio
import ray

# custom modules
from neosearch.settings import Settings
from neosearch.constants.queue import USE_QUEUE


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "tvly-...")


async def search_web(query: str) -> str:
    """Useful for using the web to answer questions."""
    client = AsyncTavilyClient(api_key=TAVILY_API_KEY)
    return str(await client.search(query))


async def record_notes(ctx: Context, notes: str, notes_title: str) -> str:
    """Useful for recording notes on a given topic. Your input should be notes with a title to save the notes under."""
    current_state = await ctx.get("state")
    if "research_notes" not in current_state:
        current_state["research_notes"] = {}
    current_state["research_notes"][notes_title] = notes
    await ctx.set("state", current_state)
    return "Notes recorded."


async def write_report(ctx: Context, report_content: str) -> str:
    """Useful for writing a report on a given topic. Your input should be a markdown formatted report."""
    current_state = await ctx.get("state")
    current_state["report_content"] = report_content
    await ctx.set("state", current_state)
    return "Report written."


async def review_report(ctx: Context, review: str) -> str:
    """Useful for reviewing a report and providing feedback. Your input should be a review of the report."""
    current_state = await ctx.get("state")
    current_state["review"] = review
    await ctx.set("state", current_state)
    return "Report reviewed."


def get_sub_agents_for_research() -> tuple[FunctionAgent, FunctionAgent, FunctionAgent]:
    llm = Settings.llm

    research_agent = FunctionAgent(
        name="ResearchAgent",
        description="Useful for searching the web for information on a given topic and recording notes on the topic.",
        system_prompt=(
            "You are the ResearchAgent that can search the web for information on a given topic and record notes on the topic. "
            "Once notes are recorded and you are satisfied, you should hand off control to the WriteAgent to write a report on the topic. "
            "You should have at least some notes on a topic before handing off control to the WriteAgent."
        ),
        llm=llm,
        tools=[search_web, record_notes],
        can_handoff_to=["WriteAgent"],
    )

    write_agent = FunctionAgent(
        name="WriteAgent",
        description="Useful for writing a report on a given topic.",
        system_prompt=(
            "You are the WriteAgent that can write a report on a given topic. "
            "Your report should be in a markdown format. The content should be grounded in the research notes. "
            "Once the report is written, you should get feedback at least once from the ReviewAgent."
        ),
        llm=llm,
        tools=[write_report],
        can_handoff_to=["ReviewAgent", "ResearchAgent"],
    )

    review_agent = FunctionAgent(
        name="ReviewAgent",
        description="Useful for reviewing a report and providing feedback.",
        system_prompt=(
            "You are the ReviewAgent that can review the write report and provide feedback. "
            "Your review should either approve the current report or request changes for the WriteAgent to implement. "
            "If you have feedback that requires changes, you should hand off control to the WriteAgent to implement the changes after submitting the review."
        ),
        llm=llm,
        tools=[review_report],
        can_handoff_to=["WriteAgent"],
    )

    return (
        research_agent, write_agent, review_agent
    )


def get_deep_research_agent() -> AgentWorkflow:
    research_agent, write_agent, review_agent = get_sub_agents_for_research()

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


def save_intermediate_result(task_id: str, event: dict):
    # save event to DB
    pass

def save_task_result(task_id: str, result: dict):
    # save result to DB
    pass


def background_research_task(task_id: str, user_msg: str):
    async def run_agent():
        agent_workflow = get_deep_research_agent()
        handler = agent_workflow.run(user_msg=user_msg)

        current_agent = None

        # 에이전트 이벤트 스트리밍
        async for event in handler.stream_events():
            if (
                hasattr(event, "current_agent_name")
                and event.current_agent_name != current_agent
            ):
                current_agent = event.current_agent_name
                print(f"\n{'='*50}")
                print(f"🤖 Agent: {current_agent}")
                print(f"{'='*50}\n")

            elif isinstance(event, AgentStream):
                if event.delta:
                    print(event.delta, end="", flush=True)
            elif isinstance(event, AgentInput):
                print("📥 Input:", event.input)
            elif isinstance(event, AgentOutput):
                if event.response.content:
                    print("📤 Output:", event.response.content)

                if event.tool_calls:
                    print(
                        "🛠️  Planning to use tools:",
                        [call.tool_name for call in event.tool_calls],
                    )

            elif isinstance(event, ToolCallResult):
                print(f"🔧 Tool Result ({event.tool_name}):")
                print(f"  Arguments: {event.tool_kwargs}")
                print(f"  Output: {event.tool_output}")

            elif isinstance(event, ToolCall):
                print(f"🔨 Calling Tool: {event.tool_name}")
                print(f"  With arguments: {event.tool_kwargs}")


        state = await handler.ctx.get("state")
        final_result = state["report_content"]

        save_task_result(task_id, final_result)

    asyncio.run(run_agent())


if not USE_QUEUE:
    # make the function ray-remote if we do not use the queue
    background_research_task = ray.remote(background_research_task)
