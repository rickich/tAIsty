from abc import ABC, abstractmethod


class IImageEmbeddingClient(ABC):
    @abstractmethod
    async def embed(self, image: str) -> list[float]:
        pass

    @abstractmethod
    async def embed_many(self, images: list[str]) -> list[list[float]]:
        pass
