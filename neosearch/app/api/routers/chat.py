from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, Request
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.llms import ChatMessage

# custom module
from neosearch.app.api.utils.chat import validate_chat_data
from neosearch.app.engine.rag_engine.chat_engine import get_chat_engine
from neosearch.app.models.chat_models import ChatData
from neosearch.app.utils.logging import Logger


logger = Logger()

# Create a router for the chat endpoint
chat_router = r = APIRouter()


@r.post("")
async def chat(
    request: Request,
    data: ChatData,
    chat_engine: BaseChatEngine = Depends(get_chat_engine),
):
    req_id = request.state.request_id
    lastMessage = await validate_chat_data(data)

    # convert messages coming from the request to type ChatMessage
    messages = [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]

    # query chat engine
    response = await chat_engine.astream_chat(lastMessage.content, messages)
    logger.log_debug(f"method={request.method} | {request.url} | {req_id} | 200 | details: Chat response generated")  # noqa: E501

    # stream response
    async def event_generator():
        async for token in response.async_response_gen():
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
