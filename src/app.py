import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.middleware import ProcessTimeMiddleware
from src.router import ingestion, retrieval


def compose_app() -> FastAPI:
    """
    Compose the FastAPI application with the defined routers.

    Returns:
        FastAPI: The FastAPI application instance.
    """
    base_path = Path(__file__).parent.parent
    tmp_path = base_path / "tmp"
    model_cache = base_path / "local_model" / "e5-small-v2"

    # creating temp_dir
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)

    # creating model cache dir
    if not os.path.exists(model_cache):
        os.mkdir(model_cache)

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(ProcessTimeMiddleware)

    app.include_router(ingestion)
    app.include_router(retrieval)

    @app.get("/")
    async def home():
        return {"message": "Welcome to data ingestion pipeline!"}

    return app
