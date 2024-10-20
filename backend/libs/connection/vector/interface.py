from abc import ABC, abstractmethod


class IVectorDBClient(ABC):
    @abstractmethod
    async def aupsert_one(self, vector: dict, namespace: str) -> dict:
        pass

    @abstractmethod
    async def aupsert(self, vectors: list[dict], namespace: str) -> list[dict]:
        pass

    @abstractmethod
    async def adelete_one(self, id: str, namespace: str) -> None:
        pass

    @abstractmethod
    async def adelete(
        self,
        ids: list[str],
        namespace: str,
    ) -> None:
        pass

    @abstractmethod
    async def adelete_all(
        self,
        namespace: str,
    ) -> None:
        pass

    @abstractmethod
    async def afind_by_id(self, id: str, namespace: str) -> dict | None:
        pass

    @abstractmethod
    async def afind(self, namespace: str, metadata_filter: dict | None = None, **kwargs: any) -> list[dict]:
        pass

    @abstractmethod
    async def aquery(
        self,
        vector: list[float],
        namespace: str,
        top_k: int = 10,
        metadata_filter: dict | None = None,
        include_metadata: bool = True,
        **kwargs: any,
    ) -> list[dict]:
        pass

    @abstractmethod
    async def akeyword_search(
        self,
        namespace: str,
        keyword_filter: dict | None = None,
        **kwargs: any,
    ) -> list[dict]:
        pass
