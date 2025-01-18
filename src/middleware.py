from fastapi import FastAPI
from fastapi.requests import Request
import time
import logging

logger = logging.getLogger('uvicorn.access')
logger.disabled = True


def register_middleware(app: FastAPI):
    @app.middleware('http')
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)
        processing_time = time.time() - start_time

        message = (
            f"{request.client.host}:{request.client.port} -  {request.method} - {request.url.path} -"
            f" {response.status_code} completed after {processing_time:.4f}"
            f" seconds")

        print(message)

        return response