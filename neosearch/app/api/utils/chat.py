from fastapi import HTTPException, status
from llama_index.core.llms import MessageRole

# custom imports
from neosearch.app.models.chat_models import ChatData


async def validate_chat_data(data: ChatData):
    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No messages provided",)  # noqa: E501
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Last message must be from user",)  # noqa: E501
    return lastMessage
