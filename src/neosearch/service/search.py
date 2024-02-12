import asyncio
import torch

# custom modules
from neosearch.ai.sbert import SentenceBert

async def execute_sbert_encode(text):
    sbert = SentenceBert()  # get singleton instance

    #TODO find way to async communication between ray serve and fastapi
    vector = await sbert(text)

    return vector

async def execute_vector_similarity_search(vector, index, k):
    pass
