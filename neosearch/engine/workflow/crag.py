from llama_index.core.workflow import (
    Workflow,
    step,
    Context,
    StartEvent,
    StopEvent,
)
from llama_index.core import (
    Document,
    PromptTemplate,
    SummaryIndex,
)
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.tools.wikipedia.base import WikipediaToolSpec
from llama_index.tools.tavily_research.base import TavilyToolSpec
from llama_index.core.base.base_retriever import BaseRetriever
from asyncio import gather

# custom modules
from neosearch.settings import Settings
from neosearch.utils.logging import Logger

from .events.crag import (
    PrepEvent,
    QueryEvent,
    RetrieveEvent,
    RelevanceEvalEvent,
    TextExtractEvent,
    RetrieveFailureEvent,
    RetrieveSuccessEvent,
    TransformQueryResultEvent,
)


logger = Logger()

# Prompt templates for the RAG workflow
_RELEVANCY_PROMPT_TEMPLATE = """As a grader, your task is to evaluate the relevance of a document retrieved in response to a user's question.

Retrieved Document:
-------------------
{context_str}

User Question:
--------------
{query_str}

Evaluation Criteria:
- Consider whether the document contains keywords or topics related to the user's question.
- The evaluation should not be overly stringent; the primary objective is to identify and filter out clearly irrelevant retrievals.

Decision:
- Assign a binary score to indicate the document's relevance.
- Use 'yes' if the document is relevant to the question, or 'no' if it is not.

Please provide your binary score ('yes' or 'no') below to indicate the document's relevance to the user question."""

# Prompt template for transforming the query
_TRANSFORM_QUERY_TEMPLATE = """Your task is to refine a query to ensure it is highly effective for retrieving relevant search results. \n
Analyze the given input to grasp the core semantic intent or meaning. \n
Original Query:
\n ------- \n
{query_str}
\n ------- \n
Your goal is to rephrase or enhance this query to improve its search performance. Ensure the revised query is concise and directly aligned with the intended search objective. \n
Respond with the optimized query only:"""


class CorrectiveRAGWorkflow(Workflow):
    """Corrective RAG Workflow."""

    @step
    async def prepare_for_retrieval(
        self, ctx: Context, ev: StartEvent,
    ) -> PrepEvent | None:
        """Prepare for retrieval."""

        query_str: str | None = ev.get("query_str")
        if query_str is None:
            return None

        tavily_ai_apikey: str | None = ev.get("tavily_ai_apikey")
        retriever = ev.get("retriever")

        # get the LLM from singleton settings
        llm = Settings.llm

        logger.log_debug("CorrectiveRAGWorkflow :: Setting up the workflow.")
        default_relevancy_prompt_template = PromptTemplate(template=_RELEVANCY_PROMPT_TEMPLATE)
        await ctx.set(
            "relevancy_pipeline",
            QueryPipeline(chain=[default_relevancy_prompt_template, llm]),
        )
        default_transform_query_template = PromptTemplate(template=_TRANSFORM_QUERY_TEMPLATE)
        await ctx.set(
            "transform_query_pipeline",
            QueryPipeline(chain=[default_transform_query_template, llm]),
        )
        await ctx.set("llm", llm)
        await ctx.set("retriever", retriever)

        # set up the tavily research tool only if the API key is provided
        if tavily_ai_apikey:
            await ctx.set("tavily_tool", TavilyToolSpec(api_key=tavily_ai_apikey))
        await ctx.set("wiki_tool", WikipediaToolSpec())

        await ctx.set("query_str", query_str)

        logger.log_debug("CorrectiveRAGWorkflow :: Prepared for retrieval.")
        return PrepEvent()


    @step
    async def retrieve(
        self, ctx: Context, ev: PrepEvent
    ) -> RetrieveEvent | None:
        """Retrieve the relevant nodes for the query."""
        query_str = await ctx.get("query_str")

        if query_str is None:
            return None

        retriever: BaseRetriever = await ctx.get("retriever", default=None)
        tavily_tool = await ctx.get("tavily_tool", default=None)
        wikipedia_tool = await ctx.get("wiki_tool", default=None)

        if not retriever or not (wikipedia_tool or tavily_tool):
            raise ValueError(
                "Retriever and tavily tool must be constructed. Run with 'documents' and 'tavily_ai_apikey' params first."
            )

        logger.log_debug("CorrectiveRAGWorkflow :: Retrieving relevant nodes.")

        try:
            # check if retriever has 'aretrieve' method
            if hasattr(retriever, "aretrieve"):
                result = await retriever.aretrieve(query_str)
            else:
                result = retriever.retrieve(query_str)

            # write the event to the stream
            ctx.write_event_to_stream(
                RetrieveSuccessEvent(msg="<evt>Retrieval successful.</evt>")
            )
        except Exception as e:
            logger.log_error(f"CorrectiveRAGWorkflow :: Retrieval failed with error: {e}")
            
            result = []
            
            # write the event to the stream
            ctx.write_event_to_stream(
                RetrieveFailureEvent(msg="<evt>Retrieval failed.</evt>")
            )

        await ctx.set("retrieved_nodes", result)
        await ctx.set("query_str", query_str)
        logger.log_debug("CorrectiveRAGWorkflow :: Retrieved relevant nodes, and ready for RetrieveEvent.")

        return RetrieveEvent(retrieved_nodes=result)


    @step
    async def eval_relevance(
        self, ctx: Context, ev: RetrieveEvent
    ) -> RelevanceEvalEvent:
        """Evaluate relevancy of retrieved documents with the query."""
        retrieved_nodes = ev.retrieved_nodes
        query_str = await ctx.get("query_str")

        # if no nodes are retrieved, set the relevancy results to an empty list
        if retrieved_nodes is None or retrieved_nodes == []:
            await ctx.set("relevancy_results", [])
            return RelevanceEvalEvent(relevant_results=[])

        # get the relevancy pipeline from the context
        relevancy_pipeline: QueryPipeline = await ctx.get("relevancy_pipeline")
        logger.log_debug("CorrectiveRAGWorkflow :: Evaluating relevance of retrieved documents.")

        # If the pipeline has an async method, use it.
        if hasattr(relevancy_pipeline, "arun"):
            # Gather the async results all at once
            gathered_results = await gather(
                [
                    relevancy_pipeline.arun(context_str=node.text, query_str=query_str)
                    for node in retrieved_nodes
                ]
            )
            relevancy_results = [result.message.content.lower().strip() for result in gathered_results]
        else:
            relevancy_results = []
            for node in retrieved_nodes:
                relevancy = relevancy_pipeline.run(
                    context_str=node.text, query_str=query_str
                )
                relevancy_results.append(relevancy.message.content.lower().strip())

        await ctx.set("relevancy_results", relevancy_results)
        return RelevanceEvalEvent(relevant_results=relevancy_results)


    @step
    async def extract_relevant_texts(
        self, ctx: Context, ev: RelevanceEvalEvent
    ) -> TextExtractEvent:
        """Extract relevant texts from retrieved documents."""
        retrieved_nodes = await ctx.get("retrieved_nodes")
        relevancy_results = ev.relevant_results

        # If any of retrieved_nodes or relevancy_results is None, return an empty string.
        if retrieved_nodes is None or relevancy_results is None or len(retrieved_nodes) == 0 or len(relevancy_results) == 0:
            return TextExtractEvent(relevant_text="")

        # If the number of retrieved nodes and relevancy results do not match, cut off the extra results.
        if len(retrieved_nodes) != len(relevancy_results):
            if len(relevancy_results) > len(retrieved_nodes):
                relevancy_results = relevancy_results[: len(retrieved_nodes)]
            else:
                relevancy_results += ["no"] * (len(retrieved_nodes) - len(relevancy_results))

        logger.log_debug("CorrectiveRAGWorkflow :: Extracting relevant texts from retrieved documents.")
        relevant_texts = [
            retrieved_nodes[i].text
            for i, result in enumerate(relevancy_results)
            if result == "yes"
        ]
        result = "\n".join(relevant_texts)
        return TextExtractEvent(relevant_text=result)


    @step
    async def transform_query_pipeline(
        self, ctx: Context, ev: TextExtractEvent
    ) -> QueryEvent:
        """Search the transformed query with Tavily API."""
        relevant_text = ev.relevant_text
        relevancy_results = await ctx.get("relevancy_results")
        query_str = await ctx.get("query_str")

        # If any document is found irrelevant, transform the query string for better search results.
        if len(relevancy_results) == 0 or "no" in relevancy_results:
            qp: QueryPipeline = await ctx.get("transform_query_pipeline")
            if hasattr(qp, "arun"):
                transformed_query_ret = await qp.arun(
                    query_str=query_str
                )
                transformed_query_str = transformed_query_ret.message.content
            else:
                transformed_query_str = qp.run(
                    query_str=query_str
                ).message.content

            # Conduct a search with the transformed query string and collect the results.
            tavily_tool = await ctx.get("tavily_tool", None)
            wikipedia_tool: WikipediaToolSpec = await ctx.get("wiki_tool")

            if tavily_tool:
                search_results = tavily_tool.search(
                    transformed_query_str, max_results=5
                )
                search_text = "\n".join([result.text for result in search_results])

                ctx.write_event_to_stream(
                    TransformQueryResultEvent(
                        msg="<evt>Transformed query generated with tavily_tool.</evt>"
                    )
                )
            elif wikipedia_tool:
                search_results = wikipedia_tool.search_data(
                    transformed_query_str, lang='en'
                )
                # search_text = "\n".join([result for result in search_results])
                if search_results == "No search results found.":
                    search_text = ""
                else:
                    search_text = search_results

                ctx.write_event_to_stream(
                    TransformQueryResultEvent(
                        msg="<evt>Transformed query generated with wikipedia_tool.</evt>"
                    )
                )
            else:
                search_text = ""
                ctx.write_event_to_stream(
                    TransformQueryResultEvent(msg="<evt>No search tool used for query transform.</evt>")
                )

        else:
            search_text = ""

        logger.log_debug(f"CorrectiveRAGWorkflow :: Transforming query using the pipeline: ({query_str} -> {transformed_query_str}) => {search_text}")
        return QueryEvent(relevant_text=relevant_text, search_text=search_text)


    @step
    async def query_result(self, ctx: Context, ev: QueryEvent) -> StopEvent:
        """Get result with relevant text."""
        relevant_text = ev.relevant_text
        search_text = ev.search_text
        query_str = await ctx.get("query_str")

        documents = [Document(text=relevant_text + "\n" + search_text)]
        index = SummaryIndex.from_documents(documents)
        query_engine = index.as_query_engine()

        if hasattr(query_engine, "aquery"):
            result = await query_engine.aquery(query_str)
        else:
            result = query_engine.query(query_str)

        logger.log_debug("CorrectiveRAGWorkflow :: Query result generated.")
        return StopEvent(result=result)


def get_corrective_rag_workflow() -> CorrectiveRAGWorkflow:
    """Get the Corrective RAG Workflow."""
    return CorrectiveRAGWorkflow()
