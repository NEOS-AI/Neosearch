import os
from tavily import AsyncTavilyClient


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "tvly-...")


async def search_web(query: str) -> str:
    """Useful for using the web to answer questions."""
    client = AsyncTavilyClient(api_key=TAVILY_API_KEY)
    tavily_search_result = await client.search(
        query,
        search_depth="basic", # "basic", advanced
        topic="general", # "general", "news"
        max_results=20,
    )
    return str(tavily_search_result)
