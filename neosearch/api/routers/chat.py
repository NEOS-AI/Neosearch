from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Request,
    status,
)

# custom module
from neosearch.engine.rag_engine.chat_engine import get_custom_chat_engine
from neosearch.engine.query_filter import generate_filters
from neosearch.models.chat_models import ChatData
from neosearch.utils.logging import Logger
from neosearch.utils.events import EventCallbackHandler
from neosearch.response.chat import ChatStreamResponse, ChatStreamResponseV2
from neosearch.settings import get_llm_model_by_id


logger = Logger()

# Create a router for the chat endpoint
chat_router = r = APIRouter()


@r.post(
    "",
    summary="Chat with the model",
    response_description="Return a stream of chat responses",
    status_code=status.HTTP_200_OK,
    response_model=ChatStreamResponse,
)
async def chat(
    request: Request,
    data: ChatData,
    background_tasks: BackgroundTasks,
) -> ChatStreamResponse:
    req_id = request.state.request_id

    try:
        last_message_content = data.get_last_message_content()
        messages = data.get_history_messages()

        # get model id, and loads the corresponding model
        model_id = data.get_model_id()
        llm = get_llm_model_by_id(model_id)

        chat_id = data.get_chat_id()

        doc_ids = data.get_chat_document_ids()
        filters = generate_filters(doc_ids)
        logger.log_info(f"method={request.method} | {request.url} | {req_id} | 200 | details: Creating chat engine with filters: {str(filters)}")  # noqa: E501

        event_handler = EventCallbackHandler()

        # get chat engine, and generate response with async chat stream
        chat_engine = get_custom_chat_engine(
            llm=llm, verbose=False
        )
        response = chat_engine.astream_chat(last_message_content, messages)

        logger.log_debug(f"method={request.method} | {request.url} | {req_id} | 200 | details: Chat response generated")  # noqa: E501

        return ChatStreamResponseV2(
            request, event_handler, response, data, background_tasks, chat_id
        )
    except Exception as e:
        logger.log_error(f"method={request.method} | {request.url} | {req_id} | 500 | details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat engine: {e}",
        ) from e


@r.post(
    "/base",
    summary="Chat with the model (base)",
    response_description="Return a stream of chat responses",
    status_code=status.HTTP_200_OK,
    response_model=ChatStreamResponse,
)
async def chat_base(
    request: Request,
    data: ChatData,
    background_tasks: BackgroundTasks,
) -> ChatStreamResponse:
    req_id = request.state.request_id

    try:
        last_message_content = data.get_last_message_content()
        messages = data.get_history_messages()

        doc_ids = data.get_chat_document_ids()
        filters = generate_filters(doc_ids)
        logger.log_info(f"method={request.method} | {request.url} | {req_id} | 200 | details: Creating chat engine with filters: {str(filters)}")  # noqa: E501

        event_handler = EventCallbackHandler()

        # get chat engine, and generate response with async chat stream
        chat_engine = get_custom_chat_engine(verbose=False)
        response = chat_engine.astream_chat(last_message_content, messages)

        logger.log_debug(f"method={request.method} | {request.url} | {req_id} | 200 | details: Chat response generated")  # noqa: E501

        return ChatStreamResponse(
            request, event_handler, response, data, background_tasks
        )
    except Exception as e:
        logger.log_error(f"method={request.method} | {request.url} | {req_id} | 500 | details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat engine: {e}",
        ) from e
