import os
from tavily import AsyncTavilyClient
from llama_index.core.workflow import Context

# custom modules
from neosearch.engine.utils.searxng import SearxngAdaptor


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "tvly-...")
WEB_SEARCH_API = os.getenv("WEB_SEARCH_API", "tavily")
SEARXNG_BASE_URL = os.getenv("SEARXNG_BASE_URL", "http://localhost:8888")


async def search_web(ctx: Context, query: str) -> str:
    """Useful for using the web to answer questions."""
    search_result = ""

    if WEB_SEARCH_API == "tavily":
        client = AsyncTavilyClient(api_key=TAVILY_API_KEY)
        search_result = await client.search(
            query,
            search_depth="basic", # "basic", advanced
            topic="general", # "general", "news"
            max_results=20,
        )
    elif WEB_SEARCH_API == "searxng":
        # searxng_search_result = await searxng_search(query)
        adaptor = SearxngAdaptor(SEARXNG_BASE_URL)
        search_result = await adaptor.asearch(query)

    if search_result != "":
        current_state = await ctx.get("state")
        current_state["web_search_result"] = search_result
        await ctx.set("state", current_state)

    return str(search_result)
