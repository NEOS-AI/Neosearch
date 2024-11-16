from fastapi import HTTPException, status

# custom imports
from neosearch.models.query_models import QueryData


async def validate_query_data(data: QueryData):
    query_data = data.query
    if query_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No query provided",
        )
    return query_data
