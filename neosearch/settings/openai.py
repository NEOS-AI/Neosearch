from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings
import os


def init_openai():
    model = os.getenv("OPENAI_MODEL", "gpt-4")
    Settings.llm = OpenAI(model=model)
