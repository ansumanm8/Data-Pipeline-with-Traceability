from langchain.schema import Document
from pydantic import BaseModel


class RetrieveDocInput(BaseModel):
    query: str


class VectorDBDocument(BaseModel):
    id: str
    page_content: str
    metadata: dict
    score: float

    @classmethod
    def from_retrieved(cls, doc: tuple[Document, float]):
        return cls(
            id=doc[0].id,
            page_content=doc[0].page_content,
            metadata=doc[0].metadata,
            score=round(doc[1], 2),
        )
