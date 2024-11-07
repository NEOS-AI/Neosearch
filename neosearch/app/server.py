from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
import os
from functools import cache
from pathlib import Path
import toml
import orjson

from starlette.responses import JSONResponse
from sqlalchemy.ext.associationproxy import _AssociationList

# custom module
from neosearch.middlewares import RequestLogger, RequestID
from neosearch.utils.logging import Logger
from neosearch.utils.gc_tuning import gc_optimization_on_startup
from neosearch.constants.trace import USE_TRACELOOP


logger = Logger()

# Traceloop (OpenTelemetry for LLM) setup
if USE_TRACELOOP:
    trace_loop_api_key = os.getenv("TRACELOOP_API_KEY", None)
    if trace_loop_api_key is not None:
        logger.log_info("Traceloop API key found. Traceloop will be enabled.")

        from traceloop.sdk import Traceloop


@cache
def project_root() -> Path:
    """Find the project root directory by locating pyproject.toml."""
    base_dir = Path(__file__).parent

    for parent_directory in base_dir.parents:
        if (parent_directory / "pyproject.toml").is_file():
            return parent_directory
    raise FileNotFoundError("Could not find project root containing pyproject.toml")


def get_version_from_pyproject_toml() -> str:
    try:
        # Probably this is the pyproject.toml of a development install
        path_to_pyproject_toml = project_root() / "pyproject.toml"
    except FileNotFoundError:
        # Probably not a development install
        path_to_pyproject_toml = None

    if path_to_pyproject_toml is not None:
        pyproject_version = toml.load(path_to_pyproject_toml)["tool"]["poetry"]["version"]
        return pyproject_version
    else:
        return os.getenv("VERSION", "x.x.x")



def default(obj):
    if isinstance(obj, _AssociationList):
        return list(obj)
    raise TypeError


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content) -> bytes:
        return orjson.dumps(content, default=default)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.get_logger()
    # gc optimization
    gc_optimization_on_startup()

    if USE_TRACELOOP and trace_loop_api_key is not None:
        # set up traceloop (OpenTelemetry for LLM)
        Traceloop.init(app_name="NeoSearch", disable_batch=False)

    yield

    # Add code to clean up the app context
    logger.log_info("Shutting down the application")


def init_app(
    use_cors: bool = False,
    cors_headers: list = ["*"],
    cors_methods: list = ["*"],
    cors_origins: list = ["*"],
) -> FastAPI:
    _version = get_version_from_pyproject_toml()
    app = FastAPI(
        title="NeoSearch",
        version=_version,
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )

    # add middlewares
    app.add_middleware(
        ProxyHeadersMiddleware, trusted_hosts="*"
    )  # add proxy headers to prevent logging IP address of the proxy server instead of the client
    app.add_middleware(GZipMiddleware, minimum_size=500)  # add gzip compression

    # add custom middlewares
    app.add_middleware(RequestLogger)
    app.add_middleware(RequestID)

    if use_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=cors_methods,
            allow_headers=cors_headers,
        )

    return app
