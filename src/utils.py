import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List

from chromadb.errors import DuplicateIDError
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

from src.exception import EmbeddingModelError
from src.model import VectorDBDocument

load_dotenv()

base_path = Path(__file__).parent.parent


class VectorDB:
    def __init__(self) -> None:
        self.embedding_model = get_embedding_model()
        self.db = Chroma(
            collection_name=os.getenv("COLLECTION_NAME"),
            embedding_function=self.embedding_model,
            persist_directory=base_path / os.getenv("VECTOR_INDEX_NAME", "demo_db"),
        )
        self._logger = get_logger()

    def add_to_vectorstore(self, documents: List[Document]):
        """
        Adds documents to the vector store.

        Args:
            documents (List[Document]): The documents to add.
        """
        self._logger.info(
            {
                "application": "VectorDatabaseOperation",
                "datetime": datetime.now(),
                "action": "Adding chunks to vector database",
            }
        )
        try:
            self.db.add_documents(documents=documents)
        except DuplicateIDError as e:
            self._logger.error(
                {
                    "application": "VectorDatabaseOperation",
                    "datetime": datetime.now(),
                    "error": e,
                }
            )
            return

    def update_vectorstore(self, documents: List[Document]):
        """
        Updates the vector store with new documents.

        Args:
            documents (List[Document]): The documents to update.
        """
        self._logger.info(
            {
                "application": "VectorDatabaseOperation",
                "datetime": datetime.now(),
                "action": "Adding chunks to existing vector database",
            }
        )
        try:
            self.add_to_vectorstore(documents)
        except DuplicateIDError as e:
            self._logger.error(
                {
                    "application": "VectorDatabaseOperation",
                    "datetime": datetime.now(),
                    "error": e,
                }
            )
            return

    def retrieve_documents(self, query: str) -> List[VectorDBDocument]:
        self._logger.info(
            {
                "application": "VectorDatabaseOperation",
                "datetime": datetime.now(),
                "action": "Retrieving chunks from vector database",
            }
        )
        retrieved_documents = self.db.similarity_search_with_relevance_scores(
            query=query, k=os.getenv("top_k", 3)
        )
        return [VectorDBDocument.from_retrieved(i) for i in retrieved_documents]


def clean_folder(folder_path: str | Path):
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"{folder} is not a valid folder")

    for item in folder.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()  # Delete file or symlink
            elif item.is_dir():
                shutil.rmtree(item)  # Recursively delete subfolder
        except Exception as e:
            print(f"Failed to delete {item}: {e}")


def get_embedding_model():
    if os.getenv("EMBEDDING_MODEL") == "huggingface":
        return HuggingFaceEmbeddings(
            model_name=os.getenv("EMBEDDING_MODEL_NAME", "intfloat/e5-small-v2")
        )
    elif os.getenv("EMBEDDING_MODEL") == "openai":
        return OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_EMBEDDING_MODEL_NAME"),
        )
    else:
        raise EmbeddingModelError(message=os.getenv("EMBEDDING_MODEL"))


# LOGGER "cache"
_LOGGER: logging.Logger | None = None


def init_logger(log_level: str = "DEBUG") -> logging.Logger:
    """
    Initialize the logger with the specified log level.
    """
    log_level = os.getenv("LOG_LEVEL", log_level)
    global _LOGGER

    logger = logging.root
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(levelname)s - %(asctime)s - %(name)s - %(message)s")
    )
    logger.handlers = [handler]
    logger.setLevel(log_level)

    _LOGGER = logger

    return logger


def get_logger() -> logging.Logger:
    global _LOGGER

    if _LOGGER:
        return _LOGGER

    _LOGGER = init_logger()

    return _LOGGER
