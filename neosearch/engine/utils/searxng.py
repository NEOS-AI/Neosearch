import httpx
import pybreaker
import aiobreaker
import asyncio
from typing import Union

# custom modules
from neosearch.constants.circuitbreaker import CB_RESET_TIMEOUT, CB_FAIL_MAX

# Global circuit breakers
g_sync_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=CB_FAIL_MAX,
    reset_timeout=CB_RESET_TIMEOUT,
    name="SearxNGCircuitBreaker_sync"
)

g_async_circuit_breaker = aiobreaker.CircuitBreaker(
    fail_max=CB_FAIL_MAX,
    timeout_duration=CB_RESET_TIMEOUT,
    name="SearxNGCircuitBreaker_async"
)


class SearxngAdaptor:
    """Searxng metasearch adaptor with circuit-breaker support."""

    def __init__(self, base_url: str):
        """
        Initialize the SearxNG Client.

        Args:
            base_url (str): base url for API call
        """
        self.base_url = base_url.rstrip("/")


    def _get_search_url(self):
        """Construct the search URL."""
        return f"{self.base_url}/search"


    def search(self, query, params:Union[dict, None]=None) -> dict:
        """
        Perform a synchronous search query using the SearxNG API.

        Args:
            query (str): The search query string.
            params (dict | None): Optional dictionary of additional parameters.

        Returns:
            (dict): JSON response with search results.
        """
        if params is None:
            params = {}

        search_url = self._get_search_url()
        search_params = {
            "q": query,
            "format": "json",
            "categories": "general,images",
            "safesearch": "1",
            "engines": "google,bing,duckduckgo,wikipedia",
            **params
        }

        @g_sync_circuit_breaker
        def execute_request():
            try:
                with httpx.Client() as client:
                    response = client.get(search_url, params=search_params)
                    response.raise_for_status()
                    return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                print(f"An error occurred: {exc}")
                raise Exception(f"An error occurred: {exc}") from exc

        return execute_request()


    async def asearch(self, query, params=None) -> dict:
        """
        Perform a synchronous search query using the SearxNG API.

        Args:
            query (str): The search query string.
            params (dict | None): Optional dictionary of additional parameters.

        Returns:
            (dict): JSON response with search results or None if an error occurs.
        """
        if params is None:
            params = {}

        search_url = self._get_search_url()
        search_params = {"q": query, "format": "json", **params}

        @g_async_circuit_breaker
        async def execute_request():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(search_url, params=search_params)
                    response.raise_for_status()
                    return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                print(f"An error occurred: {exc}")
                raise Exception(f"An error occurred: {exc}") from exc

        return await execute_request()


# Example usage
if __name__ == "__main__":
    # Replace with your SearxNG instance URL
    base_url = "https://searx.example.com"
    client1 = SearxngAdaptor(base_url)
    client2 = SearxngAdaptor(base_url)

    # Synchronous example
    query = "Python programming"
    params = {"categories": "general", "language": "en"}

    # Perform a synchronous search with client1
    print("Synchronous Search Results (Client 1):")
    results1 = client1.search(query, params)
    if results1:
        for result in results1.get("results", []):
            print(f"- {result.get('title')}: {result.get('url')}")

    # Perform a synchronous search with client2
    print("\nSynchronous Search Results (Client 2):")
    results2 = client2.search(query, params)
    if results2:
        for result in results2.get("results", []):
            print(f"- {result.get('title')}: {result.get('url')}")

    # Asynchronous example
    async def async_example():
        # Perform an asynchronous search with client1
        print("\nAsynchronous Search Results (Client 1):")
        async_results1 = await client1.asearch(query, params)
        if async_results1:
            for result in async_results1.get("results", []):
                print(f"- {result.get('title')}: {result.get('url')}")

        # Perform an asynchronous search with client2
        print("\nAsynchronous Search Results (Client 2):")
        async_results2 = await client2.search_async(query, params)
        if async_results2:
            for result in async_results2.get("results", []):
                print(f"- {result.get('title')}: {result.get('url')}")

    asyncio.run(async_example())
