from contextlib import asynccontextmanager
from fastapi import FastAPI
import os
from functools import cache
from pathlib import Path
import toml

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.settings import Settings

# custom module
from neosearch.app.utils.logging import Logger
from neosearch.app.utils.gc_tuning import gc_optimization_on_startup

logger = Logger()


def init_settings():
    model = os.getenv("MODEL", "gpt-4")
    Settings.llm = OpenAI(model=model)
    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-small", embed_batch_size=100
    )
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20


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

    #TODO open redis connection for lifespan
    yield

    #TODO: Add code to clean up the app context
