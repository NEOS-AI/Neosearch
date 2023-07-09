from fastapi import FastAPI, Form
from elasticsearch import Elasticsearch
from pydantic import BaseModel
from typing import Annotated

# custom modules
from semantic_search_fastapi.encoder import Encoder
from semantic_search_fastapi.utils import create_es_index, create_faiss_index, es_search, faiss_search


index_name = "corpus"

es = Elasticsearch(["localhost:9200"])
es_indices = create_es_index(es, index=index_name)

encoder = Encoder("small", dimension=256)
faiss_indices = create_faiss_index(encoder)


app = FastAPI()

class SearchQuery(BaseModel):
    query: str

class SearchResponse(BaseModel):
    elastic: list
    faiss: list

@app.post("/search")
async def search(query:SearchQuery) -> SearchResponse:
    es_result = es_search(es, index=index_name, query=query.query)
    faiss_result = faiss_search(encoder, faiss_indices, query)
    result = SearchResponse(elastic=es_result, faiss=faiss_result)
    return result


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
