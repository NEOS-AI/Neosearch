from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
import os
from functools import cache
from pathlib import Path
from traceloop.sdk import Traceloop
import toml

# custom module
from neosearch.app.middlewares import RequestLogger, RequestID
from neosearch.app.utils.logging import Logger
from neosearch.app.utils.gc_tuning import gc_optimization_on_startup


logger = Logger()

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.get_logger()
    # gc optimization
    gc_optimization_on_startup()

    # set up traceloop (OpenTelemetry for LLM)
    Traceloop.init(app_name="NeoSearch", disable_batch=False)

    #TODO open redis connection for lifespan
    yield

    #TODO: Add code to clean up the app context


def init_app() -> FastAPI:
    _version = get_version_from_pyproject_toml()
    app = FastAPI(title="NeoSearch", version=_version, lifespan=lifespan)

    # add middlewares
    app.add_middleware(
        ProxyHeadersMiddleware, trusted_hosts="*"
    )  # add proxy headers to prevent logging IP address of the proxy server instead of the client
    app.add_middleware(GZipMiddleware, minimum_size=500)  # add gzip compression

    # add custom middlewares
    app.add_middleware(RequestLogger)
    app.add_middleware(RequestID)

    return app