from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, Request
import asyncio

# custom module
from neosearch.engine.utils.query import validate_query_data
from neosearch.engine.workflow.crag import CorrectiveRAGWorkflow, get_corrective_rag_workflow
from neosearch.constants.memory import MAX_MEMORY_TOKEN_SIZE
from neosearch.engine.rag_engine.query_engine import RAGStringQueryEngine, get_string_query_engine
from neosearch.models.query_models import QueryData, MemoryResponse
from neosearch.utils.logging import Logger


logger = Logger()

# Create a router for the chat endpoint
search_router = r = APIRouter()

@r.post("")
async def query_for_search(
    request: Request,
    data: QueryData,
    query_engine: RAGStringQueryEngine = Depends(get_string_query_engine),
):
    req_id = request.state.request_id
    query = await validate_query_data(data)
    retriever = query_engine.retriever

    # get the query response
    response = await query_engine.aquery(query, retriever)

    logger.log_debug(f"method={request.method} | {request.url} | {req_id} | 200 | details: Query response generated")  # noqa: E501

    # stream response
    async def event_generator():
        async for token in response.async_response_gen():
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")


@r.post("/crag")
async def query_for_crag(
    request: Request,
    data: QueryData,
    query_engine: RAGStringQueryEngine = Depends(get_string_query_engine),
    workflow: CorrectiveRAGWorkflow = Depends(get_corrective_rag_workflow),
):
    req_id = request.state.request_id
    query = await validate_query_data(data)
    retriever = query_engine.retriever

    # run the workflow
    task = workflow.run(
        query_str=query,
        retriever=retriever,
    )

    logger.log_debug(f"method={request.method} | {request.url} | {req_id} | 200 | details: Query response generated")  # noqa: E501

    # stream response
    async def event_generator():
        async for ev in workflow.stream_events():
            logger.info(f"Sending message to frontend: {ev.msg}")
            yield f"{ev.msg}\n\n"
            await asyncio.sleep(0.1)  # Small sleep to ensure proper chunking

        response = await task
        async for token in response.async_response_gen():
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")


@r.get("/memory")
async def memory_info(request: Request,):
    """
    Provides the memory information (stored memory, memory max tokens, and memory number of tokens).
    Inspired by the ChatGPT backend API (https://chatgpt.com/backend-api/memories?include_memory_entries=false).

    Returns:
        MemoryResponse: The memory response.
    """
    req_id = request.state.request_id
    logger.log_debug(f"method={request.method} | {request.url} | {req_id} | 200 | details: Memory response generated")

    #TODO check memory info

    return MemoryResponse(messages=[], memory_max_tokens=MAX_MEMORY_TOKEN_SIZE, memory_num_tokens=0)
