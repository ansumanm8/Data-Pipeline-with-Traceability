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
    tmp_path = Path(__file__).parent.parent / "tmp"

    # creating temp_dir
    if not os.path.exists(tmp_path):
        print("Temp not found creating.....")
        os.mkdir(tmp_path)

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
