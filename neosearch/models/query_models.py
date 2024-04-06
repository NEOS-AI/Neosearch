from pydantic import BaseModel


class QueryData(BaseModel):
    query: str
