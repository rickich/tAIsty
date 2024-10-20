from libs.connection.vector.interface import IVectorDBClient
from libs.service.vector import FetchVector, MatchVector, Vector


class VectorDatabaseService:
    def __init__(self, vector_db_client: IVectorDBClient):
        self._client = vector_db_client

    async def find_by_id(
        self,
        entity_id: str,
        namespace: str | None = None,
    ) -> Vector | None:
        vec = await self._client.afind_by_id(id=entity_id, namespace=namespace)
        if not vec:
            return None
        return Vector(**vec)

    async def find(
        self,
        filter: dict | None = None,
        namespace: str | None = None,
    ) -> list[FetchVector] | None:
        if filter == {}:
            vecs = await self._client.afind(metadata_filter={})
        else:
            vecs = await self._client.afind(namespace=namespace, metadata_filter=filter)
        if not vecs:
            return None
        return [FetchVector(**vec) for vec in vecs]

    async def upload(
        self,
        entity: Vector,
        namespace: str | None = None,
    ) -> Vector:
        vec = await self._client.aupsert_one(vector=entity.model_dump(mode="json"), namespace=namespace)
        return Vector(**vec)

    async def delete(self, entity_id: str, namespace: str | None = None) -> None:
        await self._client.adelete_one(id=entity_id, namespace=namespace)

    async def delete_all(self, namespace: str | None = None) -> None:
        await self._client.adelete_all(namespace=namespace)

    async def query(
        self,
        vector: list[float],
        top_k: int,
        metadata_filter: dict | None = None,
        namespace: str | None = None,
    ) -> list[MatchVector]:
        matches = await self._client.aquery(
            vector=vector,
            namespace=namespace,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )
        return [MatchVector(**match) for match in matches]

    async def keyword_search(
        self,
        keyword_filter: dict | None = None,
        namespace: str | None = None,
        **kwargs,
    ) -> list[dict]:
        """
        키워드 검색을 수행합니다.
        keyword_filter 예시:
        {
            "metadata.ingredients": [{
                "keyword": "egg",
                "action": "must_not"
            }]
        }
        """
        matches = await self._client.akeyword_search(
            namespace=namespace,
            keyword_filter=keyword_filter,
            **kwargs,
        )
        return matches
