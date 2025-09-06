import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, BackgroundTasks, Form, UploadFile, status
from fastapi.responses import JSONResponse

from src.model import RetrieveDocInput, VectorDBDocument
from src.service import DataIngestionService
from src.utils import VectorDB, clean_folder, get_logger

executor = ThreadPoolExecutor()

base_path = Path(__file__).parent.parent
logger = get_logger()


ingestion = APIRouter(tags=["Ingestion"])
retrieval = APIRouter(tags=["Document Retrieval"])

ALLOWED_TYPES = ["application/pdf", "text/csv", "text/plain"]


@ingestion.post("/ingest")
async def ingest_data(
    file: UploadFile, background_task: BackgroundTasks, column_name: str = Form(None)
):
    logger.info(
        {
            "application": "IngestionRouter",
            "datetime": datetime.now(),
            "action": "Ingestion Pipeline Triggered",
        }
    )
    if file.content_type not in ALLOWED_TYPES:
        logger.error(
            {
                "application": "IngestionRouter",
                "datetime": datetime.now(),
                "error": "Unsupported file received",
            }
        )
        raise JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Unsupported file type. Please upload a PDF, CSV, or text file."  # noqa: E501
            },
        )

    if file.content_type == "text/csv" and column_name == "":
        logger.error(
            {
                "application": "IngestionRouter",
                "datetime": datetime.now(),
                "error": "Required column name not provided",
            }
        )
        raise JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content={
                "message": "Unprocessable CSV's require a column name for processing"
            },
        )

    temporary_fp = base_path / "tmp"
    file_path = temporary_fp / file.filename

    service = DataIngestionService(
        file_path=file_path,
        filename=file.filename,
        file_type=file.content_type,
        file=file,
        column_name=column_name if file.content_type == "text/csv" else None,
    )

    #  Storing the file in a temporary location for further processing
    await service.tmp_file_write(file=file, file_path=file_path)

    # Running the ingestion pipeline in the background
    logger.error(
        {
            "application": "IngestionRouter",
            "datetime": datetime.now(),
            "action": "Background process started for ingestion",
        }
    )
    background_task.add_task(service.run)

    # Remove the file from the temporary storage location
    background_task.add_task(clean_folder, temporary_fp)

    return JSONResponse(
        content={"message": "Data ingestion pipeline initiated successfully."},
        status_code=202,
    )


@retrieval.post("/retrieve/docs")
async def get_documents(data: RetrieveDocInput) -> List[VectorDBDocument]:
    service = VectorDB()
    logger.info(
        {
            "application": "Retrieval router",
            "datetime": datetime.now().isoformat(),
            "action": "Document retrieval started",
        }
    )
    loop = asyncio.get_event_loop()
    docs = await loop.run_in_executor(executor, service.retrieve_documents, data.query)
    return JSONResponse(
        content={
            # Explicit serialization due to customization
            "documents": [i.model_dump() for i in docs]
        },
        status_code=status.HTTP_200_OK,
    )
