from fastapi import APIRouter, Request, Response


api = APIRouter()

@api.get("/search")
async def search(request: Request) -> Response:
    return {"message": "Hello World"}
