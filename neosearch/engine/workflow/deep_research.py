from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import (
    Workflow,
    Context,
    StartEvent,
    StopEvent,
    step,
)

# custom modules
from neosearch.engine.agents.deep_research import get_deep_research_agent

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

        agent_workflow: AgentWorkflow = get_deep_research_agent()
        await ctx.set("agent_workflow", agent_workflow)

        return PrepEvent()

    @step
    async def run_research_agent(
        self, ctx: Context, ev: PrepEvent,
    ) -> None:
        """Run the research agent."""
        query_str: str = await ctx.get("query_str")
        agent_workflow: AgentWorkflow = await ctx.get("agent_workflow")

        # run the research agent
        result = await agent_workflow.run(
            user_msg=query_str,
            ctx=ctx,
        )

        return StopEvent(result=result)
