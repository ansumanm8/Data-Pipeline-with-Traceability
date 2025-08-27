import mimetypes
import os
import pathlib

import pytest
from fastapi.testclient import TestClient

from src.app import compose_app
from src.model import RetrieveDocInput

app = compose_app()

client = TestClient(app)

base_dir = pathlib.Path("tests/mock_data")

params = os.listdir(base_dir)


@pytest.fixture(params=params)
def file_upload_fixture(request):
    file_path = base_dir / request.param
    return file_path


def test_home_default():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to data ingestion pipeline!"}


def test_retrieve_document():
    query = "AI and its impact in IT"
    payload = RetrieveDocInput(query=query).model_dump()
    response = client.post("/retrieve/docs", json=payload)
    print(response)
    assert response.status_code == 200
    assert response.json() is not None


# Happy Path
def test_upload_file_acceptance(file_upload_fixture):
    file_name = file_upload_fixture.name
    mime_type, _ = mimetypes.guess_type(file_name)
    with open(file_upload_fixture, "rb") as f:
        files = {"file": (file_upload_fixture.name, f, mime_type)}
        response = client.post(
            "/ingest",
            files=files,
            data={"column_name": "ArtistName"}
            if mime_type == "text/csv"
            else {"column_name": None},
        )

    assert response.status_code == 202
    json_data = response.json()

    assert json_data["message"] == "Data ingestion pipeline initiated successfully."
