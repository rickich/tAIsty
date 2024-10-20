import argparse
import base64

from dotenv import load_dotenv
from openai import OpenAI
from pydantic_settings import BaseSettings


class OpenAIClientSettings(BaseSettings):
    api_key: str
    endpoint: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"
    max_tokens: int = 1000

    class Config:
        env_prefix = "OPENAI_"


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, required=True, help="Image path (jpeg)")
    args = parser.parse_args()

    load_dotenv(override=True)
    settings = OpenAIClientSettings()

    client = OpenAI(
        api_key=settings.api_key,
        base_url=settings.endpoint,
    )

    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Provide accurate information, ask for clarification when needed, and admit when you don't know something. Be polite and respectful at all times.",
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(args.image)}",
                    },
                },
            ],
        },
    ]
    stream = client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        messages=messages,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices:
            print(chunk.choices[0].delta.content or "", end="", flush=True)
