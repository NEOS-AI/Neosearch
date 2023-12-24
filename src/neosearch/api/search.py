from fastapi import APIRouter, Request, Response


api = APIRouter()

@api.get("/search")
async def search(request: Request) -> Response:
    #TODO validate request
    #TODO execute search (request to Ray Serve)
    #TODO return response
    return {"message": "Hello World"}
