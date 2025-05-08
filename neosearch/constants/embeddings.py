# Use Ollama embeddings for true, otherwise use fastembed
# Claude, Grok does not support embeddings, so we use either Ollama or FastEmbed
USE_OLLAMA_FOR_DEFAULT_EMBEDDING = True

OLLAMA_EMBEDDING_MODEL_BASE = "llama2"
