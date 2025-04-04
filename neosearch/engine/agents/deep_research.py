import asyncio
import orjson
from llama_index.core.agent.workflow import (
    FunctionAgent,
    AgentInput,
    AgentOutput,
    ToolCall,
    ToolCallResult,
    AgentStream,
)

# custom modules
from neosearch.settings import Settings
from neosearch.utils.ray import ray_remote_if_enabled
from neosearch.engine.prompts.deep_research import (
    DEEP_RESEARCH_GENERATE_QUESTIONS,
    DEEP_RESEARCH_TOPIC_AND_DOMAIN_GETTER,
    DEEP_RESEARCH_SUMMARY_SYSTEM_PROMPT,
)

from .research import get_research_workflow_agent
from .tools import save_generate_questions


def _get_topic_and_domain_getter_agent(llm) -> FunctionAgent:
    return FunctionAgent(
        name="TopicAndDomainGetterAgent",
        description="Useful for extracting the topic and domain from the context.",
        system_prompt=DEEP_RESEARCH_TOPIC_AND_DOMAIN_GETTER,
        llm=llm,
        tools=[],
        can_handoff_to=["QueryGeneratorAgent"],
    )

def _get_query_generator_agent(llm, topic: str, domain: str) -> FunctionAgent:
    prompt = str(DEEP_RESEARCH_GENERATE_QUESTIONS)
    prompt = prompt.replace("{topic}", topic)
    prompt = prompt.replace("{domain}", domain)
    return FunctionAgent(
        name="QueryGeneratorAgent",
        description="Useful for generating questions to guide the research agent.",
        system_prompt=prompt,
        llm=llm,
        tools=[save_generate_questions],
        can_handoff_to=["ResearchAgent"],
    )


def _get_query_generator_agent_for_deep_research_summary(llm, user_msg: str, results: list[str]) -> FunctionAgent:
    results_formatted = [f"- {result}" for result in results]
    results_str = "\n".join(results_formatted)

    prompt = str(DEEP_RESEARCH_SUMMARY_SYSTEM_PROMPT).format(
        user_msg=user_msg,
        results=results_str,
    )

    return FunctionAgent(
        name="DeepResearchSummaryAgent",
        description="Agent for generating a final summary of the research.",
        system_prompt=prompt,
        llm=llm,
        tools=None,
        can_handoff_to=None,
    )


async def save_intermediate_event_to_db(task_id: str, event: dict):
    # save event to DB
    pass

async def save_intermediate_result(task_id: str, result: str):
    # save event to DB
    pass

async def save_task_result(task_id: str, result: str):
    # save result to DB
    pass


async def run_research_query_generation(task_id: str, user_msg: str):
    llm = Settings.llm
    topic_and_domain_getter_agent = _get_topic_and_domain_getter_agent(llm)
    handler = topic_and_domain_getter_agent.run(user_msg=user_msg)

    topic = None
    domain = None
    async for event in handler.stream_events():
        if isinstance(event, AgentOutput):
            if event.response.content:
                result = event.response.content
                result_obj: dict = orjson.loads(result)
                topic = result_obj.get("topic", user_msg)
                domain = result_obj.get("domain", "general")
    print(f"📌 Extracted Topic: {topic}")
    print(f"📌 Extracted Domain: {domain}")

    # after extract topic and domain, generate questions
    query_generate_agent = _get_query_generator_agent(llm, topic, domain)
    handler_ = query_generate_agent.run(user_msg=user_msg)

    async for event in handler_.stream_events():
        if isinstance(event, AgentOutput):
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

    state = await handler_.ctx.get("state")
    questions = state["questions"]

    questions_obj = {
        "topic": topic,
        "domain": domain,
        "questions": questions,
    }
    questions_str = orjson.dumps(questions_obj).decode("utf-8")
    save_intermediate_result(task_id, questions_str)

    return questions


async def run_research_agent_for_query(task_id: str, query: str):
    agent_workflow = get_research_workflow_agent()
    handler = agent_workflow.run(user_msg=query)

    current_agent = None

    # Agent event streaming (async generator)
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

    # save the intermediate result to DB
    save_intermediate_result(task_id, final_result)

    return final_result


async def summarize_deep_research(task_id: str, user_msg: str, results: list[str]) -> str:
    llm = Settings.llm
    summary_agent = _get_query_generator_agent_for_deep_research_summary(
        llm, user_msg, results
    )

    handler = summary_agent.run(user_msg=user_msg)
    final_result = None

    async for event in handler.stream_events():
        if isinstance(event, AgentOutput):
            if event.response.content:
                print("📤 Output:", event.response.content)
                final_result = event.response.content

        elif isinstance(event, AgentInput):
            print("📥 Input:", event.input)

    if final_result is None:
        return "❗ No final result generated."

    return final_result


@ray_remote_if_enabled
def background_research_task(task_id: str, user_msg: str):
    async def run_agent():
        questions = await run_research_query_generation(task_id, user_msg)
        results = []
        for query in questions:
            print(f"\n{'='*50}")
            print(f"🔍 Query: {query}")
            print(f"{'='*50}\n")

            final_result = await run_research_agent_for_query(task_id, query)
            results.append(final_result)

        # summarize the results
        final_result = await summarize_deep_research(task_id, user_msg, results)
        await save_task_result(task_id, final_result)

    asyncio.run(run_agent())
