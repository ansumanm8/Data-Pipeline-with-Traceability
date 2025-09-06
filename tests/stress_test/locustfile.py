import logging

from locust import FastHttpUser, between, task

from src.model import RetrieveDocInput

logging.getLogger("urllib3").setLevel(logging.WARNING)


class FastAPIUser(FastHttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def home(self):
        self.client.get("/")

    @task
    def search(self):
        query = "AI and its impact in IT"
        payload = RetrieveDocInput(query=query).model_dump()
        self.client.post("/retrieve/docs", json=payload)
