import asyncio
import base64
import json
from typing import Optional
import httpx


def convert_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def fetch_and_display(
    session_id: str,
    message: str,
    limit: int,
    image_path: Optional[str] = None,
):
    url = "http://localhost:8000/api/v1/chat"

    # form-data로 보낼 데이터 설정
    data = {
        "session_id": session_id,
        "message": message,
        "limit": str(limit),  # form-data에서는 정수도 문자열로 전송
    }

    # 파일 업로드 설정 (이미지가 있다면 추가)
    if image_path:
        data["image"] = convert_image_to_base64(image_path)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=data)
        print(response.json()["message"])

    print("\nChat closed")


if __name__ == "__main__":
    # 테스트 데이터 입력
    asyncio.run(
        fetch_and_display(
            session_id="41c380a1-ba76-4713-9032-110ee94488dp",
            message="And also i have allergies to Eggs and Soy",
            # message="I don't like spicy food",
            limit=10,
            # image_path="artifacts/ttuckpokki.jpg",  # 이미지 파일 경로를 지정하거나 None으로 둠
        )
    )
