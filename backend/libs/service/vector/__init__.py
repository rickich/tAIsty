from pydantic import BaseModel


class Vector(BaseModel):
    id: str
    values: list[float]
    metadata: dict[str, str | int | bool | float | dict | list | None]


class MatchVector(BaseModel):
    id: str
    score: float
    metadata: dict[str, str | int | bool | float | dict | list | None]


class FetchVector(BaseModel):
    id: str
    metadata: dict[str, str | int | bool | float | dict | list | None]
