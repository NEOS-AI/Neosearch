import asyncio
import torch

# custom modules
from neosearch.ai.sbert import SentenceBert


def encode_with_sbert(text):
    sbert = SentenceBert()
    model = sbert.get_model()
    with torch.no_grad():
        return model.encode(text)

async def execute_sbert_encode(text):
    sbert = SentenceBert()  # get singleton instance

    #TODO find way to async communication between ray serve and fastapi

    # init asyncio event loop and process pool
    loop = asyncio.get_event_loop()
    pool = sbert.get_process_pool()

    # run encode_with_sbert in process pool and return the result
    vector = await loop.run_in_executor(pool, encode_with_sbert, text=text)
    return vector

async def execute_vector_similarity_search(vector, index, k):
    pass
