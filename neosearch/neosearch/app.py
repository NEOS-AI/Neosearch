from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

# custom modules
from neosearch.middlewares.request_logger import RequestLogger
from neosearch.middlewares.request_id import RequestID
# from neosearch.api import base64_router, hex_router, sha256_router


def init_app(use_rate_limitter:bool=False):
    app = FastAPI()

    if use_rate_limitter:
        from neosearch.utils.ratelimitter import limiter

        # add rate limitter
        app.state.limitter = limiter

    # add middlewares
    app.add_middleware(
        ProxyHeadersMiddleware, trusted_hosts="*"
    )  # add proxy headers to prevent logging IP address of the proxy server instead of the client
    app.add_middleware(GZipMiddleware, minimum_size=500)  # add gzip compression

    # add custom middlewares
    app.add_middleware(RequestLogger)
    app.add_middleware(RequestID)

    # set up static files (css, js, images, etc.)
    app.mount("/public", StaticFiles(directory="public"), name="public")

    return app


# def add_api_routers(app:FastAPI):
#     app.include_router(base64_router, prefix="/base64")
