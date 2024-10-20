import json
import numpy as np
from collections.abc import AsyncGenerator
from typing import Literal

from app.chat.application.service.chat_history_service import ChatHistoryService
from app.chat.domain.entity.chat_history import ChatHistoryMessage
from app.chat.utils.parse import (
    parse_additional_preferences,
    parse_function_calls,
    parse_preferences_or_restrictions,
    parse_remove_function_calls,
)
from libs.connection.embedding.image.interface import IImageEmbeddingClient
from libs.service.llm import ChatMessage
from libs.service.llm.llm_completion import LLMCompletionService
from libs.service.prompt.interface import IPromptManager
from libs.service.vector.vector_db import VectorDatabaseService
from libs.sse.message import AssistantMessage, SSEMessage


class ChatbotService:
    def __init__(
        self,
        llm_service: LLMCompletionService,
        chat_history_service: ChatHistoryService,
        prompt_manager: IPromptManager,
        vector_db_service: VectorDatabaseService,
        image_embedding_client: IImageEmbeddingClient,
    ):
        self._llm_service = llm_service
        self._chat_history_service = chat_history_service
        self._prompt_manager = prompt_manager
        self._vector_db_service = vector_db_service
        self._image_embedding_client = image_embedding_client
        self.last_recommendation = None

    def _construct_metadata_filter(self, preferences: dict, action: Literal["must", "must_not", "should"]) -> dict:
        metadata_filter = {}
        for key, value in preferences.items():
            metadata_filter[f"metadata.{key}"] = []
            for v in value:
                metadata_filter[f"metadata.{key}"].append(
                    {
                        "action": action,
                        "value": v,
                    }
                )

        return metadata_filter

    async def search_menu(
        self,
        condition: dict,
        image_content: str | None = None,
        is_remove: bool = False,
        top_k: int = 3,
    ) -> list[dict]:
        action = "must_not" if is_remove else "must"
        random = False
        if image_content:
            image_embedding = await self._image_embedding_client.embed(image_content)

            # search menu by image
            match_vectors = await self._vector_db_service.query(
                vector=image_embedding,
                top_k=top_k,
                metadata_filter=self._construct_metadata_filter(condition, action),
            )
            return [v.metadata for v in match_vectors], random

        # search menu by condition
        matches = await self._vector_db_service.find(filter=self._construct_metadata_filter(condition, action))
        if not matches:
            matches = await self._vector_db_service.find({}, action)
            random = True
        np.random.shuffle(matches)  # random shuffle
        return [match.metadata for match in matches][:top_k], random

    async def get_user_preferences(self, user_message: str) -> dict:
        # function calling
        # get condition from user message
        prompt = self._prompt_manager.get_prompt("get_user_preferences")
        messages = prompt.compile(user_message=user_message)
        chat_message = prompt.get_chat_messages(messages)
        system_prompt = prompt.get_system_prompt(messages)
        resp = await self._llm_service.run_nlp_task(
            chat_messages=chat_message, system_prompt=system_prompt, **prompt.parameters
        )
        return parse_function_calls(resp)

    async def get_user_dispreferences(self, user_message: str) -> dict:
        # function calling
        # get condition from user message
        prompt = self._prompt_manager.get_prompt("remove_user_preferences")
        messages = prompt.compile(user_message=user_message)
        chat_message = prompt.get_chat_messages(messages)
        system_prompt = prompt.get_system_prompt(messages)
        resp = await self._llm_service.run_nlp_task(
            chat_messages=chat_message, system_prompt=system_prompt, **prompt.parameters
        )
        return parse_remove_function_calls(resp)

    async def run_planner(self, user_message: str) -> bool:
        prompt = self._prompt_manager.get_prompt("planner")
        messages = prompt.compile(user_message=user_message)
        chat_message = prompt.get_chat_messages(messages)
        system_prompt = prompt.get_system_prompt(messages)
        resp = await self._llm_service.run_nlp_task(
            chat_messages=chat_message, system_prompt=system_prompt, **prompt.parameters
        )
        return resp.startswith("ADD")

    async def generate_stream_response(
        self,
        session_id: str,
        user_message: str,
        image_content: str | None = None,  # base64 or image url
        image_type: Literal["jpeg", "png"] | None = None,
        limit: int = 10,
    ) -> AsyncGenerator[str, None]:
        """메인 로직
        1. ChatHistoryService를 통해 채팅 히스토리를 불러옵니다.
        2. 유저 메시지로부터 function calling을 진행한 뒤, condition을 받습니다.
        3. condition을 통해 메뉴를 검색합니다.
        3. 최종 결과를 스트리밍 형태로 반환합니다.
        4. ChatHistoryService를 통해 채팅 히스토리를 업데이트합니다."""
        await self._chat_history_service.load_chat_histories(session_id, limit)
        is_prefer = await self.run_planner(user_message)

        if is_prefer:
            print("prefer")
            preferences = await self.get_user_preferences(user_message)
            print(preferences)
            menus, random_recommend = await self.search_menu(preferences, image_content)
            print(menus)
        else:
            print("dislike")
            preferences = await self.get_user_dispreferences(user_message)
            print(preferences)
            menus, random_recommend = await self.search_menu(preferences, image_content, is_remove=True)
            print(menus)

        print(menus)
        recommended_products = ", ".join([menu["name"] for menu in menus])
        if random_recommend:
            recommended_products += (
                "\n\nBe sure to mention that I recommended it to you because nothing else met your preferences!\n"
            )

        # construct input variables
        input_variables = {
            "user_preferences": parse_preferences_or_restrictions(preferences),
            "recommended_products": recommended_products,
            "additional_preferences": parse_additional_preferences(preferences),
        }
        print("input_variables")
        print(input_variables)

        # construct content
        content = self._construct_input_content(user_message)

        async for stream_response in self.create_final_stream_response(session_id, content, input_variables):
            yield stream_response

    async def generate_response(
        self,
        session_id: str,
        user_message: str,
        image_content: str | None = None,  # base64 or image url
        image_type: Literal["jpeg", "png"] | None = None,
        limit: int = 10,
    ) -> dict:
        """메인 로직
        1. ChatHistoryService를 통해 채팅 히스토리를 불러옵니다.
        2. 유저 메시지로부터 function calling을 진행한 뒤, condition을 받습니다.
        3. condition을 통해 메뉴를 검색합니다.
        3. 최종 결과를 스트리밍 형태로 반환합니다.
        4. ChatHistoryService를 통해 채팅 히스토리를 업데이트합니다."""
        await self._chat_history_service.load_chat_histories(session_id, limit)
        is_prefer = await self.run_planner(user_message)

        if is_prefer:
            preferences = await self.get_user_preferences(user_message)
            print(preferences)
            menus, random_recommend = await self.search_menu(preferences, image_content)
            print(menus)
        else:
            preferences = await self.get_user_dispreferences(user_message)
            print(preferences)
            menus, random_recommend = await self.search_menu(preferences, image_content, is_remove=True)
            print(menus)

        recommended_products = "\n".join([f"{idx+1}. {menu['name']}" for idx, menu in enumerate(menus)])
        self.last_recommendation = recommended_products
        if random_recommend:
            print("@" * 99)
            recommended_products += (
                "\n\nSince there were no dishes that matched your preferences, I recommended these menu items!\n"
            )

        recommendations = [
            {
                "name": menu["name"],
                "category": menu["category"],
                "file": menu["file"],
            }
            for menu in menus
        ]

        # construct input variables
        input_variables = {
            "user_preferences": parse_preferences_or_restrictions(preferences),
            "recommended_products": recommended_products,
            "additional_preferences": parse_additional_preferences(preferences),
        }
        # construct content
        content = self._construct_input_content(user_message)

        return await self.create_final_response(session_id, content, input_variables, recommendations)

    async def create_final_response(
        self,
        session_id: str,
        content: str | list[dict] | None = None,
        input_variables: dict | None = None,
        recommendations: list[dict] | None = None,
    ) -> dict:
        # add User message
        if content:
            await self._chat_history_service.update_chat_history(session_id, role="user", content=content)

        prompt = self._prompt_manager.get_prompt(prompt_name="recommendation")
        input_variables = input_variables or {}
        print("input_variables")
        print(input_variables)
        messages = prompt.compile(**input_variables)

        system_prompt = prompt.get_system_prompt(messages)
        chat_history_messages = self._chat_history_service.chat_history_messages[-3:]

        final_response = await self._llm_service.run_nlp_task(
            chat_messages=(
                [ChatMessage(**message.model_dump(mode="json")) for message in chat_history_messages]
                if chat_history_messages
                else None
            ),
            system_prompt=system_prompt,
            **prompt.parameters,
        )

        await self._chat_history_service.update_chat_history(session_id, "assistant", final_response)
        return {"message": final_response, "recommendations": recommendations}

    async def create_final_stream_response(
        self,
        session_id: str,
        content: str | list[dict] | None = None,
        input_variables: dict | None = None,
    ) -> AsyncGenerator[str, None]:

        # add User message
        if content:
            await self._chat_history_service.update_chat_history(session_id, role="user", content=content)

        prompt = self._prompt_manager.get_prompt(prompt_name="recommendation")
        input_variables = input_variables or {}
        messages = prompt.compile(**input_variables)
        system_prompt = prompt.get_system_prompt(messages)

        chat_history_messages = self._chat_history_service.chat_history_messages[-3:]

        final_response_parts = []
        async for stream_response in self._stream_wrapper(
            final_response_parts,
            system_prompt=system_prompt,
            chat_history_messages=chat_history_messages,
            **prompt.parameters,
        ):
            yield stream_response

        # add Assistant message
        final_response = "".join(final_response_parts)
        await self._chat_history_service.update_chat_history(session_id, "assistant", final_response)

    async def _stream_wrapper(
        self,
        final_response_parts: list,
        system_prompt: str | None = None,
        chat_history_messages: list[ChatHistoryMessage] | None = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:

        async for chunk in self._llm_service.run_nlp_task_stream(
            system_prompt=system_prompt,
            chat_messages=(
                [ChatMessage(**message.model_dump(mode="json")) for message in chat_history_messages]
                if chat_history_messages
                else None
            ),  # data type conversion (ChatHistoryMessage -> ChatMessage)
            **kwargs,
        ):
            yield self._normal_streaming_response(final_response_parts, chunk)

    def _make_image_url(self, image_content: str, image_type: Literal["jpeg", "png"]) -> str:
        if image_type == "url":
            return image_content
        return f"data:image/{image_type};base64,{image_content}"

    def _construct_input_content(self, user_message: str, images: list[dict] | None = None) -> list[dict]:
        if not images:
            return user_message

        content = [{"type": "text", "text": user_message}]
        for image in images:
            content.append(
                {
                    "type": "image",
                    "url": self._make_image_url(image["content"], image["type"]),
                }
            )
        return content

    @staticmethod
    def _normal_streaming_response(final_response_parts: list, chunk: str) -> str:
        final_response_parts.append(chunk)
        data = AssistantMessage(content=chunk)
        current_content = json.dumps(data, default=lambda x: x.__dict__, ensure_ascii=False)
        return f"data: {current_content}\n\n"

    @staticmethod
    def _item_streaming_response(item_type: str, item: str) -> str:
        data = SSEMessage(role=item_type, content=item)
        current_content = json.dumps(data, default=lambda x: x.__dict__, ensure_ascii=False)
        return f"data: {current_content}\n\n"
