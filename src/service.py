from datetime import datetime
from typing import Optional

from src.data_ingestion import DataIngestionPipeline
from src.utils import get_logger


class DataIngestionService:
    def __init__(
        self,
        file_path: str,
        filename: str,
        file_type: str,
        file,
        column_name: Optional[str] = None,
    ):
        self.file_path = file_path
        self.filename = filename
        self.file_type = file_type
        self.column_name = column_name
        self.file = file
        self._logger = get_logger()

    async def tmp_file_write(self, file, file_path: str):
        self._logger.info(
            {
                "application": "DataIngestionService",
                "datetime": datetime.now(),
                "action": "Writing file to Temporary directory",
            }
        )
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

    async def run(self):
        ingestion_service = DataIngestionPipeline(
            file_path=self.file_path,
            filename=self.filename,
            file_type=self.file_type,
            column_name=self.column_name,
        )
        ingestion_service.run()
