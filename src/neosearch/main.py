from fastapi import Request
import sys
from ray import serve

# configure the directory name functions as a package
sys.path.append("..")

# custom modules
from neosearch.ai.sbert import sbert_app  # noqa: E402
from neosearch.app import init_app  # noqa: E402
from neosearch.utils import Logger  # noqa: E402

# init fastapi
app = init_app(use_rate_limitter=True)
logger = Logger()

# start up event
@app.on_event("startup")
async def startup_event() -> None:
    logger.get_logger()  # init logger before app starts up

    #TODO find way to run ray serve with custom grpc options

    # start ray serve with custom http options
    serve.start(http_options={"host": "0.0.0.0", "port": 10518})

    # deploy sbert app
    serve.create_backend("sbert", sbert_app)
    serve.create_endpoint("sbert", backend="sbert")


# shutdown event
@app.on_event("shutdown")
async def shutdown_event() -> None:
    pass


@app.get("/")
async def root(request: Request) -> dict:
    req_id = request.state.request_id
    logger.log_debug(f"Request ID: {req_id} :: Request Root")
    return {"message": "Hello World"}


if __name__ == "__main__":
    try:
        import uvicorn

        uvicorn.run("main:app", host="0.0.0.0", port=8518, log_level="warning", reload=True)
    except ImportError:
        print("Uvicorn is not installed. Install it with `pip install uvicorn`.")
