"""
DATA PIPELINE

This module provides functionality to process and embed text data from various sources file of type as follows:
    - CSV
    - Text
    - PDF

It includes functions for pre-processing data, creating document chunks, and embedding text.
"""  # noqa: E501
import hashlib
from datetime import datetime
from typing import List, Optional, Union

import pandas as pd
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from pandas import DataFrame

from src.utils import VectorDB, get_logger


class DataIngestionPipeline:
    """
    A class to handle the data ingestion pipeline.

    Attributes:
        embedding_model (SentenceTransformer): The model used for text embedding.
    """

    def __init__(
        self,
        file_path: str,
        filename: str,
        file_type: str,
        column_name: Optional[str] = None,
    ):
        self.file_path = file_path
        self.filename = filename
        self.file_type = file_type
        self.column_name = column_name
        self.db = VectorDB()
        self._logger = get_logger()

    def read_file(self) -> Union[List[Document], DataFrame]:
        """
        Reads the file based on its type and returns the data.

        Returns:
            Union[List[Document], DataFrame]: The data read from the file.
        """
        if self.file_type == "text/csv":
            self._logger.info(
                {
                    "application": "DataIngestionPipeline",
                    "datetime": datetime.now().isoformat(),
                    "action": "Reading CSV",
                }
            )
            return pd.read_csv(self.file_path)
        elif self.file_type == "text/plain":
            self._logger.info(
                {
                    "application": "DataIngestionPipeline",
                    "datetime": datetime.now().isoformat(),
                    "action": "Reading Plain text file",
                }
            )
            return TextLoader(self.file_path).load()
        elif self.file_type == "application/pdf":
            self._logger.info(
                {
                    "application": "DataIngestionPipeline",
                    "datetime": datetime.now().isoformat(),
                    "action": "Reading PDF file",
                }
            )
            return PyPDFLoader(self.file_path).load()
        else:
            self._logger.error(
                {
                    "application": "DataIngestionPipeline",
                    "datetime": datetime.now().isoformat(),
                    "error": f"{self.file_type}",
                }
            )
            raise ValueError("Unsupported file type. Use 'csv', 'text', or 'pdf'.")

    def pre_processing_csv(
        self, filename: str, data: DataFrame, column_name: str
    ) -> List[Document]:
        self._logger.info(
            {
                "application": "DataIngestionPipeline",
                "datetime": datetime.now().isoformat(),
                "action": "Started CSV preprocessing",
            }
        )
        return [
            Document(
                id=hashlib.sha256(desc.encode("utf-8")).hexdigest(),
                page_content=desc,
                metadata={
                    **{k: v for k, v in row.items() if k != column_name},
                    "source": filename,
                    "creationdate": datetime.now().isoformat(),
                },
            )
            for desc, row in zip(data[column_name], data.to_dict(orient="records"))
        ]

    def pre_processing_text(
        self, filename: str, data: List[Document]
    ) -> List[Document]:
        self._logger.info(
            {
                "application": "DataIngestionPipeline",
                "datetime": datetime.now().isoformat(),
                "action": f"Starting {self.file_type} preprocessing",
            }
        )
        for doc in data:
            doc.id = hashlib.sha256(doc.page_content.encode("utf-8")).hexdigest()
            doc.metadata["source"] = filename
            doc.metadata["creationdate"] = datetime.now().isoformat()

        return data

    def create_chunks(self, data: Union[List[Document], DataFrame]) -> List[Document]:
        if self.file_type == "text/csv":
            return self.pre_processing_csv(
                filename=self.filename, data=data, column_name=self.column_name
            )
        elif self.file_type in ["text/plain", "application/pdf"]:
            self._logger.info(
                {
                    "application": "DataIngestionPipeline",
                    "datetime": datetime.now().isoformat(),
                    "action": "Chunking document",
                }
            )
            return RecursiveCharacterTextSplitter(
                chunk_size=500, chunk_overlap=100
            ).split_documents(
                self.pre_processing_text(filename=self.filename, data=data)
            )
        else:
            self._logger.info(
                {
                    "application": "DataIngestionPipeline",
                    "datetime": datetime.now().isoformat(),
                    "action": "Chunking document",
                }
            )
            raise ValueError("Unsupported document type. Use 'csv', 'text', or 'pdf'.")

    def run(self):
        self._logger.info(
            {
                "application": "DataIngestionPipeline",
                "datetime": datetime.now().isoformat(),
                "action": "DataIngestionPipeline started",
            }
        )
        data = self.read_file()
        chunks = self.create_chunks(data)
        start_time = datetime.now()
        self.db.add_to_vectorstore(chunks)
        end_time = datetime.now()
        self._logger.info(
            {
                "application": "DataIngestionPipeline",
                "datetime": datetime.now().isoformat(),
                "action": f"Total time taken for processing ingestion pipeline - {end_time-start_time} /s",  # noqa: E501
            }
        )
        return
