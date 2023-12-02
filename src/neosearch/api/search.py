from fastapi import APIRouter, Request, Response, status


api = APIRouter()

@api.get("/search")
async def search(request: Request) -> Response:
    return {"message": "Hello World"}
