from dotenv import load_dotenv
import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback

# Load environment variables
load_dotenv()

# Add the root directory to the path so that we can import the settings
sys.path.append("..")

# custom module
from neosearch.api.routers.chat import chat_router  # noqa: E402
from neosearch.settings import init_settings  # noqa: E402
from neosearch.app.server import init_app  # noqa: E402
from neosearch.utils.logging import Logger  # noqa: E402


app: FastAPI = init_app()
init_settings()

environment = os.getenv("ENVIRONMENT", "dev")  # Default to 'development' if not set
logger = Logger()

app.include_router(chat_router, prefix="/api/chat")


#
# exception handling
#

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    # log the traceback and return 500
    logger.log_error(f"method={request.method} | {request.url} | {request.state.request_id} | 500 | details: {traceback.format_exc()}")
    return {"detail": "Internal Server Error"}, 500

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request, exc):
    await log_http_exception(request, exc)
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    await log_http_exception(request, exc)
    return {"detail": exc.detail}, exc.status_code

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    exc.detail = exc.errors()
    await log_http_exception(request, exc)
    return {"detail": exc.detail}, 400

async def log_http_exception(request, exc):
    logger.log_warning(f"method={request.method} | {request.url} | {request.state.request_id} | {exc.status_code} | details: {exc.detail}")


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", reload=True)
