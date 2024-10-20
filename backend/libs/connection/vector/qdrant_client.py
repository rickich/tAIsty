from qdrant_client import AsyncQdrantClient, models

from libs.connection.vector.interface import IVectorDBClient


class QdrantClient(IVectorDBClient):
    def __init__(self, api_key: str, url: str, collection_name: str, dimension: int):
        self.client = AsyncQdrantClient(api_key=api_key, url=url)
        self.collection_name = collection_name
        self.dimension = dimension

    async def initialize(self):
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=self.dimension, distance=models.Distance.COSINE),
            )

    async def aupsert_one(self, vector: dict, namespace: str | None = None) -> dict:
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[models.PointStruct(id=vector["id"], vector=vector["values"], payload=vector["metadata"])],
        )
        return vector

    async def aupsert(self, vectors: list[dict], namespace: str | None = None) -> list[dict]:
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(id=vector["id"], vector=vector["values"], payload=vector["metadata"])
                for vector in vectors
            ],
        )
        return vectors

    async def adelete_one(self, id: str, namespace: str | None = None) -> None:
        await self.client.delete(collection_name=self.collection_name, points_selector=[id])

    async def adelete(self, ids: list[str], namespace: str | None = None) -> None:
        await self.client.delete(collection_name=self.collection_name, points_selector=ids)

    async def adelete_all(self, namespace: str | None = None) -> None:
        await self.client.delete_collection(collection_name=self.collection_name)

    async def afind_by_id(self, id: str, namespace: str | None = None) -> dict | None:
        raise NotImplementedError

    async def aupdate_metadata(self, id: str, metadata: dict, namespace: str | None = None) -> dict:
        await self.client.set_payload(
            collection_name=self.collection_name,
            payload=metadata,
            points=[id],
        )

    async def akeyword_search(
        self,
        namespace: str | None = None,
        keyword_filter: dict | None = None,
        **kwargs,
    ):
        query_filter = None
        if keyword_filter:
            query_filter = self._construct_keyword_query_filter(keyword_filter)

        resp: models.QueryResponse = await self.client.query_points(
            collection_name=self.collection_name,
            query_filter=query_filter,
            with_payload=True,
            with_vectors=False,
            **kwargs,
        )

        return [
            {
                "id": point.id,
                "metadata": point.payload,
            }
            for point in resp.points
        ]

    async def afind(
        self,
        namespace: str | None = None,
        metadata_filter: dict | None = None,
        **kwargs,
    ) -> list[dict]:
        query_filter = None
        if metadata_filter:
            query_filter = self._construct_metadata_query_filter(metadata_filter)

        resp: models.QueryResponse = await self.client.query_points(
            collection_name=self.collection_name,
            query_filter=query_filter,
            with_payload=True,
            with_vectors=False,
            **kwargs,
        )

        return [
            {
                "id": point.id,
                "metadata": point.payload,
            }
            for point in resp.points
        ]

    async def aquery(
        self,
        vector: list[float],
        namespace: str | None = None,
        top_k: int = 10,
        metadata_filter: dict | None = None,
        include_metadata: bool = True,
        **kwargs,
    ):
        query_filter = None
        if metadata_filter:
            query_filter = self._construct_metadata_query_filter(metadata_filter)

        resp: list[models.ScoredPoint] = await self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=query_filter,
            limit=top_k,
            append_payload=include_metadata,
            **kwargs,
        )
        return [
            {
                "id": point.id,
                "score": point.score,
                "metadata": point.payload,
            }
            for point in resp
        ]

    def _construct_keyword_query_filter(self, keyword_filter: dict) -> models.Filter:
        """keyword_filter 예시:
        {
            "key1": [
                {"action": "must", "keyword": "keyword1"},
                {"action": "must_not", "keyword": "keyword2"},
            ],
            "key2": [
                {"action": "should", "keyword": "keyword3"},
            ],
        }

        """
        must = []
        must_not = []
        should = []

        for key, conditions in keyword_filter.items():
            for condition in conditions:
                action = condition["action"]
                keyword = condition["keyword"]

                field_condition = models.FieldCondition(key=key, match=models.MatchText(text=keyword))
                if action == "must":
                    must.append(field_condition)
                elif action == "must_not":
                    must_not.append(field_condition)
                elif action == "should":
                    should.append(field_condition)

        return models.Filter(must=must, must_not=must_not, should=should)

    def _construct_metadata_query_filter(self, metadata_filter: dict) -> models.Filter:
        """metadata_filter 예시:
        {
            "metadata.key1": [
                {"value": "value1", "action": "must"},
                {"value": "value2", "action": "must_not"},
            ],
            "metadata.key2": [
                {"value": "value3", "action": "must"},
            ],
        }

        """

        must = []
        must_not = []
        should = []

        for key, conditions in metadata_filter.items():
            for condition in conditions:
                action = condition["action"]
                value = condition["value"]
                field_condition = models.FieldCondition(key=key, match=models.MatchValue(value=value))
                if action == "must":
                    must.append(field_condition)
                elif action == "must_not":
                    must_not.append(field_condition)
                elif action == "should":
                    should.append(field_condition)

        return models.Filter(must=must, must_not=must_not, should=should)
