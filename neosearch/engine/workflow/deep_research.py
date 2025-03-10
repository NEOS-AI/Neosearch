from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.agent.workflow.workflow_events import AgentInput
from llama_index.core.workflow import (
    Workflow,
    Context,
    StartEvent,
    StopEvent,
    step,
)

# custom modules
from neosearch.engine.agents.deep_research import get_deep_research_agent
from neosearch.engine.prompts.deep_research import DEEP_RESEARCH_GENERATE_QUESTIONS

from .events.deep_research import PrepEvent


class DeepResearchWorkflow(Workflow):

    @step
    async def prepare_for_research(
        self, ctx: Context, ev: StartEvent,
    ) -> PrepEvent | None:
        """Prepare for research."""
        query_str: str | None = ev.get("query_str")
        if query_str is None:
            return None

        ctx.set("query_str", query_str)

        agent_workflow: AgentWorkflow = get_deep_research_agent(query_str)
        await ctx.set("agent_workflow", agent_workflow)

        return PrepEvent()

    @step
    async def generate_topics(self, ctx: Context, ev: PrepEvent):
        """Generate topics for the research."""
        query_str: str = await ctx.get("query_str")

        #TODO query generation 에이전트를 만들고, 에이전트를 통해 사용자 쿼리를 여러개의 sub_query (혹은 steps)로 나누어서 처리한다.
        print(DEEP_RESEARCH_GENERATE_QUESTIONS)
        agent_workflow: AgentWorkflow = await ctx.get("agent_workflow")
        event = AgentInput(
            input=query_str,
            current_agent_name=ev.current_agent_name,
        )
        agent_workflow.run_agent_step(ctx, event)


    @step
    async def run_research_agent(
        self, ctx: Context, ev: PrepEvent,
    ) -> None:
        """Run the research agent."""
        agent_workflow: AgentWorkflow = await ctx.get("agent_workflow")
        result = await agent_workflow.run(ctx)
        return StopEvent(result=result)
