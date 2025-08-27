class EmbeddingModelError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(
            f"Unsupported embedding model: '{message}'. Only Huggingface and OpenAI models are supported."  # noqa: E501
        )
