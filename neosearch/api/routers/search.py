from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, Request
from llama_index.core.query_engine import CustomQueryEngine, TransformQueryEngine
from typing import Union

# custom module
from neosearch.api.utils.query import validate_query_data
from neosearch.app.rag import get_rag_searcher, RagSearcher
from neosearch.engine.rag_engine.query_engine import get_query_engine
from neosearch.models.query_models import QueryData
from neosearch.utils.logging import Logger


logger = Logger()

# Create a router for the chat endpoint
search_router = r = APIRouter()

@r.post("")
async def query_for_search(
    request: Request,
    data: QueryData,
    query_engine: Union[
        CustomQueryEngine,
        TransformQueryEngine
    ] = Depends(get_query_engine),
    rag_searcher: RagSearcher = Depends(get_rag_searcher),
):
    req_id = request.state.request_id
    query = await validate_query_data(data)

    #TODO use rag_searcher to search results from external search engines

    # query to the engine
    response = await query_engine.aquery(query.query)
    logger.log_debug(f"method={request.method} | {request.url} | {req_id} | 200 | details: Query response generated")  # noqa: E501

    # stream response
    async def event_generator():
        async for token in response.async_response_gen():
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
