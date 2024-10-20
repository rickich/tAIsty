from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration

from app.chat.application.service.chat_history_service import ChatHistoryService
from app.chat.application.service.chatbot_service import ChatbotService
from app.chat.infrastructure.persistence.sqlalchemy.chat_history import (
    RDBChatHistoryRepo,
)
from libs.connection.embedding.image.clip_embedding_client import CLIPEmbeddingClient
from libs.connection.llm.openai_client import OpenAIClient
from libs.connection.vector.qdrant_client import QdrantClient
from libs.service.llm.llm_completion import LLMCompletionService
from libs.service.prompt.yaml_prompt_manager import YamlPromptManager
from libs.service.vector.vector_db import VectorDatabaseService


class Container(DeclarativeContainer):
    wiring_config = WiringConfiguration(packages=["app"])

    config = providers.Configuration()

    # connection
    openai_client = providers.Singleton(
        OpenAIClient,
        api_key=config.openai.api_key,
        endpoint=config.openai.endpoint,
        model=config.openai.model,
        max_tokens=config.openai.max_tokens,
    )

    chat_history_repo = providers.Singleton(RDBChatHistoryRepo)
    prompt_manager = providers.Singleton(YamlPromptManager, prompts_dir=config.prompt.prompts_dir)
    clip_embedding_client = providers.Singleton(
        CLIPEmbeddingClient,
        model=config.clip_embedding.model,
    )

    qdrant_client = providers.Singleton(
        QdrantClient,
        api_key=config.qdrant.api_key,
        url=config.qdrant.url,
        collection_name=config.qdrant.collection_name,
        dimension=config.qdrant.dimension,
    )

    vector_db_service = providers.Singleton(VectorDatabaseService, vector_db_client=qdrant_client)

    chat_history_service = providers.Factory(ChatHistoryService, chat_history_repository=chat_history_repo)

    chat_llm_service = providers.Factory(LLMCompletionService, client=openai_client)
    chatbot_service = providers.Factory(
        ChatbotService,
        llm_service=chat_llm_service,
        chat_history_service=chat_history_service,
        prompt_manager=prompt_manager,
        vector_db_service=vector_db_service,
        image_embedding_client=clip_embedding_client,
    )
