from llama_index.llms.ollama import Ollama
from llama_index.core.settings import Settings
import os


def init_ollama():
    model = os.getenv("OLLAMA_MODEL", "mixtral")
    Settings.llm = Ollama(model=model)
