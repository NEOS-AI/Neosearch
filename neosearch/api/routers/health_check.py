from fastapi import APIRouter, status

# custom module
from neosearch.models.health_check import HealthCheck
from neosearch.utils.logging import Logger


logger = Logger()

# Create a router for the chat endpoint
health_router = r = APIRouter()


@r.get(
    "",
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
async def health_check() -> dict:
    """
    Health check endpoint to verify the API is running.
    """
    return HealthCheck(status="OK")
