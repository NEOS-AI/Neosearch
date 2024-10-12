from pydantic import BaseModel
from datetime import datetime

# custom module
from neosearch.constants.memory import MAX_MEMORY_TOKEN_SIZE


class QueryData(BaseModel):
    query: str
    timezone: str = "UTC"


class Memory(BaseModel):
    """
    Memory model.

    Attributes:
        id (str): The memory ID. (ULID based)
        updated_at (str): The updated timestamp.
        content (str): The content of the memory.
    """
    id: str
    updated_at: str = datetime.now().isoformat()
    content: str

class MemoryResponse(BaseModel):
    """
    Memory data model.
    This represents the memory data model, which contains the additional memory data.

    Attributes:
        messages (list[Memory]): The list of messages.
        memory_max_tokens (int): The maximum memory tokens.
        memory_num_tokens (int): The number of memory tokens that are currently in use (cannot exceed memory_max_tokens).
    """
    messages: list[Memory]
    memory_max_tokens: int = MAX_MEMORY_TOKEN_SIZE
    memory_num_tokens: int = 0
