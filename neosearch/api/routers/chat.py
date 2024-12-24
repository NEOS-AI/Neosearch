from fastapi import APIRouter, BackgroundTasks, Request, HTTPException, status

# custom module
from neosearch.engine.rag_engine.chat_engine import get_custom_chat_engine
from neosearch.engine.query_filter import generate_filters
from neosearch.models.chat_models import ChatData
from neosearch.utils.logging import Logger
from neosearch.utils.events import EventCallbackHandler
from neosearch.response.chat import ChatStreamResponse


# Create a router for the chat endpoint
chat_router = r = APIRouter()

logger = Logger()


@r.post("")
async def chat(
    request: Request,
    data: ChatData,
    background_tasks: BackgroundTasks,
):
    req_id = request.state.request_id

    try:
        last_message_content = data.get_last_message_content()
        messages = data.get_history_messages()

        doc_ids = data.get_chat_document_ids()
        filters = generate_filters(doc_ids)
        # params = data.data or {}
        logger.log_info(f"method={request.method} | {request.url} | {req_id} | 200 | details: Creating chat engine with filters: {str(filters)}")  # noqa: E501

        event_handler = EventCallbackHandler()
        chat_engine = get_custom_chat_engine(last_message_content, messages, verbose=False)
        response = chat_engine.astream_chat(last_message_content, messages)

        logger.log_debug(f"method={request.method} | {request.url} | {req_id} | 200 | details: Chat response generated")  # noqa: E501

        return ChatStreamResponse(
            request, event_handler, response, data, background_tasks
        )
    except Exception as e:
        logger.log_error("Error in chat engine", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat engine: {e}",
        ) from e
