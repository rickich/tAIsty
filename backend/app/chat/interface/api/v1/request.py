from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Session ID", example="41c380a1-ba76-4713-9032-110ee94488dp")
    message: str = Field(..., description="User's Message", example="Hello")
    limit: int = Field(10, ge=1, le=10, description="Number of maximum chat history", example=10)
    image: str | None = Field(
        None,
        description="Base64-encoded image",
        example="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/4QAWRXhpZgAATU0AKgAAAAgAA1IBAAABAAEA",
    )
