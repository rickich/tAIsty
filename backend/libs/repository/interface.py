from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from core.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class IBaseRepo(ABC, Generic[ModelType, SchemaType]):
    @abstractmethod
    async def get_all(self) -> list[SchemaType]:
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> SchemaType | None:
        pass

    @abstractmethod
    async def create(self, schema: SchemaType) -> SchemaType:
        pass

    @abstractmethod
    async def update_by_id(
        self,
        entity_id: int,
        params: dict,
    ) -> SchemaType:
        pass

    @abstractmethod
    async def delete_by_id(self, entity_id: int) -> None:
        pass
