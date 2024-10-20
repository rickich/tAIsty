from abc import ABC, abstractmethod

from libs.service.prompt import Prompt


class IPromptManager(ABC):
    @abstractmethod
    def get_prompt(self, prompt_name: str) -> Prompt:
        pass
