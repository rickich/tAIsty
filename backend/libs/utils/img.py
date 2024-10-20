import base64
import re
from typing import Literal

import requests


def convert_image_bytes_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def download_image_url(image_url: str) -> bytes:
    response = requests.get(image_url)
    return response.content


def detect_image_format(base64_string: str) -> Literal["PNG", "JPEG"]:
    # Base64 문자열에서 헤더 부분 추출 (데이터 URL 형식일 수 있음)
    header_match = re.match(r"^data:image/(\w+);base64,", base64_string)

    if header_match:
        # data URL 형식인 경우, 형식을 반환
        return header_match.group(1).upper()

    # data URL 형식이 아닐 경우, 순수 Base64 데이터 디코딩
    try:
        image_data = base64.b64decode(base64_string)
    except Exception:
        raise ValueError("Invalid Base64 string.")

    # 이미지 형식에 따른 파일 헤더 검사
    if image_data[:8] == b"\x89PNG\r\n\x1a\n":
        return "PNG"
    elif image_data[:3] == b"\xff\xd8\xff":
        return "JPEG"
    else:
        raise ValueError("Unsupported image format.")
