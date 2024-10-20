import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(override=True)


class OpenAIClientSettings(BaseSettings):
    api_key: str
    endpoint: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"
    max_tokens: int = 1000

    class Config:
        env_prefix = "OPENAI_"


class ClipEmbeddingClientSettings(BaseSettings):
    model: str = "ViT-B/32"


class PromptManagerSettings(BaseSettings):
    prompts_dir: str = "prompts"


class QdrantClientSettings(BaseSettings):
    api_key: str
    url: str
    collection_name: str
    dimension: int = 512

    class Config:
        env_prefix = "QDRANT_"


class Config(BaseSettings):
    env: str = "development"
    debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    db_url: str = "sqlite+aiosqlite:///./test.db"
    sentry_sdn: str = ""

    openai: OpenAIClientSettings = OpenAIClientSettings()
    prompt: PromptManagerSettings = PromptManagerSettings()
    qdrant: QdrantClientSettings = QdrantClientSettings()
    clip_embedding: ClipEmbeddingClientSettings = ClipEmbeddingClientSettings()


class TestConfig(Config):
    db_url: str = "sqlite+aiosqlite:///./test.db"


class LocalConfig(Config):
    pass


class ProductionConfig(Config):
    DEBUG: bool = False


def get_config():
    env = os.getenv("ENV", "local")
    config_type = {
        "test": TestConfig(),
        "local": LocalConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
