from llama_index.core.workflow import Event
from llama_index.core.schema import NodeWithScore


class PrepEvent(Event):
    """Prep event (prepares for retrieval)."""

    pass


class RetrieveEvent(Event):
    """Retrieve event (gets retrieved nodes)."""

    retrieved_nodes: list[NodeWithScore]


class RelevanceEvalEvent(Event):
    """Relevance evaluation event (gets results of relevance evaluation)."""

    relevant_results: list[str]


class TextExtractEvent(Event):
    """Text extract event. Extracts relevant text and concatenates."""

    relevant_text: str


class QueryEvent(Event):
    """Query event. Queries given relevant text and search text."""

    relevant_text: str
    search_text: str


# streaming events

class CragStreamingEvents(Event):
    msg: str

class RetrieveSuccessEvent(CragStreamingEvents):
    pass

class RetrieveFailureEvent(CragStreamingEvents):
    pass

class TransformQueryResultEvent(CragStreamingEvents):
    pass
