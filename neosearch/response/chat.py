import orjson
from typing import Awaitable, List

from aiostream import stream
from fastapi import BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from llama_index.core.chat_engine.types import StreamingAgentChatResponse
from llama_index.core.schema import NodeWithScore

# custom modules
from neosearch.utils.events import EventCallbackHandler
from neosearch.utils.logging import Logger
from neosearch.services.next_question_suggesion import NextQuestionSuggestion
from neosearch.models.chat_models import ChatData, Message, SourceNodes


logger = Logger()


class ChatStreamResponse(StreamingResponse):
    """
    Class to convert the response from the chat engine to the streaming format expected by Chat
    """

    TEXT_PREFIX = "0:"
    DATA_PREFIX = "8:"
    ERROR_PREFIX = "3:"

    def __init__(
        self,
        request: Request,
        event_handler: EventCallbackHandler,
        response: Awaitable[StreamingAgentChatResponse],
        chat_data: ChatData,
        background_tasks: BackgroundTasks,
    ):
        content = ChatStreamResponse.content_generator(
            request, event_handler, response, chat_data, background_tasks
        )
        super().__init__(content=content)


    @classmethod
    async def content_generator(
        cls,
        request: Request,
        event_handler: EventCallbackHandler,
        response: Awaitable[StreamingAgentChatResponse],
        chat_data: ChatData,
        background_tasks: BackgroundTasks,
    ):
        chat_response_generator = cls._chat_response_generator(
            response, background_tasks, event_handler, chat_data
        )
        event_generator = cls._event_generator(event_handler)

        # Merge the chat response generator and the event generator
        combine = stream.merge(chat_response_generator, event_generator)
        is_stream_started = False
        try:
            async with combine.stream() as streamer:
                async for output in streamer:
                    if await request.is_disconnected():
                        break

                    if not is_stream_started:
                        is_stream_started = True
                        # Stream a blank message to start displaying the response in the UI
                        yield cls.convert_text("")

                    yield output
        except Exception:
            logger.exception("Error in stream response")
            yield cls.convert_error(
                "An unexpected error occurred while processing your request, preventing the creation of a final answer. Please try again."
            )
        finally:
            # Ensure event handler is marked as done even if connection breaks
            event_handler.is_done = True


    @classmethod
    async def _event_generator(cls, event_handler: EventCallbackHandler):
        """
        Yield the events from the event handler
        """
        async for event in event_handler.async_event_gen():
            event_response = event.to_response()
            if event_response is not None:
                yield cls.convert_data(event_response)


    @classmethod
    async def _chat_response_generator(
        cls,
        response: Awaitable[StreamingAgentChatResponse],
        background_tasks: BackgroundTasks,
        event_handler: EventCallbackHandler,
        chat_data: ChatData,
    ):
        """
        Yield the text response and source nodes from the chat engine
        """
        # Wait for the response from the chat engine
        result = await response

        # Once we got a source node, start a background task to download the files (if needed)
        cls._process_response_nodes(result.source_nodes, background_tasks)

        # Yield the source nodes
        yield cls.convert_data(
            {
                "type": "sources",
                "data": {
                    "nodes": [
                        SourceNodes.from_source_node(node).model_dump()
                        for node in result.source_nodes
                    ]
                },
            }
        )

        final_response = ""
        async for token in result.async_response_gen():
            final_response += token
            yield cls.convert_text(token)

        # Generate next questions if next question prompt is configured
        question_data = await cls._generate_next_questions(
            chat_data.messages, final_response
        )
        if question_data:
            yield cls.convert_data(question_data)

        # the text_generator is the leading stream, once it's finished, also finish the event stream
        event_handler.is_done = True

    @classmethod
    def convert_text(cls, token: str) -> str:
        # Escape newlines and double quotes to avoid breaking the stream
        token = orjson.dumps(token).decode("utf-8")
        return f"{cls.TEXT_PREFIX}{token}\n"

    @classmethod
    def convert_data(cls, data: dict) -> str:
        data_str = orjson.dumps(data).decode("utf-8")
        return f"{cls.DATA_PREFIX}[{data_str}]\n"

    @classmethod
    def convert_error(cls, error: str) -> str:
        error_str = orjson.dumps(error).decode("utf-8")
        return f"{cls.ERROR_PREFIX}{error_str}\n"

    @staticmethod
    def _process_response_nodes(
        source_nodes: List[NodeWithScore],
        background_tasks: BackgroundTasks,
    ):
        try:
            # Start background tasks to download documents from LlamaCloud if needed
            from app.engine.service import LLamaCloudFileService  # type: ignore

            LLamaCloudFileService.download_files_from_nodes(
                source_nodes, background_tasks
            )
        except ImportError:
            logger.debug(
                "LlamaCloud is not configured. Skipping post processing of nodes"
            )
            pass

    @staticmethod
    async def _generate_next_questions(chat_history: List[Message], response: str):
        questions = await NextQuestionSuggestion.suggest_next_questions(
            chat_history, response
        )
        if questions:
            return {
                "type": "suggested_questions",
                "data": questions,
            }
        return None


class ChatStreamResponseV2(ChatStreamResponse):
    def __init__(self, request, event_handler, response, chat_data, background_tasks, chat_id: str):
        super().__init__(request, event_handler, response, chat_data, background_tasks)

        self.chat_id = chat_id
