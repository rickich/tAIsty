from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, select, update

from core.db.session import Base, session_factory
from libs.repository.interface import IBaseRepo

ModelType = TypeVar("ModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class RDBBaseRepo(IBaseRepo[ModelType, SchemaType]):

    def __init__(self, model: type[ModelType], schema: type[SchemaType]):
        self.model = model
        self.schema = schema

    def to_schema(self, model: ModelType) -> SchemaType:
        return self.schema.model_validate(model)

    def from_schema(self, schema: SchemaType) -> ModelType:
        return self.model(**schema.dict())

    async def get_all(self) -> list[SchemaType]:
        async with session_factory() as session:
            query = select(self.model)
            result = await session.execute(query)
        return [self.to_schema(item) for item in result.scalars().all()]

    async def get_by_id(self, entity_id: int) -> SchemaType | None:
        async with session_factory() as session:
            query = select(self.model).where(self.model.id == entity_id)
            result = await session.execute(query)
            item = result.scalars().first()
        return self.to_schema(item) if item else None

    async def create(self, schema: SchemaType) -> SchemaType:
        async with session_factory() as session:
            model = self.from_schema(schema)
            session.add(model)
            await session.commit()
            await session.refresh(model)
        return self.to_schema(model)

    async def update_by_id(
        self,
        entity_id: int,
        params: dict,
    ) -> None:
        async with session_factory() as session:
            query = update(self.model).where(self.model.id == entity_id).values(**params)
            await session.execute(query)
            await session.commit()

    async def delete_by_id(
        self,
        entity_id: int,
    ) -> None:
        async with session_factory() as session:
            query = delete(self.model).where(self.model.id == entity_id)
            await session.execute(query)
            await session.commit()
