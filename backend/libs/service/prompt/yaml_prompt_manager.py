from pathlib import Path

from libs.service.llm import ChatMessage
from libs.service.prompt import Prompt
from libs.service.prompt.exceptions import PromptNotFoundError, PromptReadError
from libs.service.prompt.interface import IPromptManager
from libs.service.prompt.utils.read_yaml import read_yaml


class YamlPromptManager(IPromptManager):
    """로컬 프롬프트 루트 디렉토리로부터 프롬프트를 로드하고, 추론 시 프롬프트를 이름으로서 가져오는 클래스입니다.

    초기화시 제공된 prompts_dir 디렉토리로부터 프롬프트(yaml)를 읽습니다. (반드시 자식 디렉토리에 있을 필요는 없음)

    프롬프트 이름은 프롬프트 파일명 (.yaml 확장자 제외) 입니다."""

    def __init__(self, prompts_dir: str):

        self._prompts_dir = prompts_dir
        self._prompt_map = self._load_prompt_map(prompts_dir)

    def get_prompt(self, prompt_name: str) -> Prompt:
        """로드된 프롬프트 맵에서 주어진 이름의 프롬프트를 가져옵니다.

        Args:
            prompt_name (str): 가져올 프롬프트의 이름.

        Returns:
            Prompt: 주어진 이름의 프롬프트 객체.
        """
        if prompt_name not in self._prompt_map:
            raise PromptNotFoundError(f"Prompt not found: {prompt_name}")
        return self._prompt_map[prompt_name]

    def _load_prompt(self, prompt_name: str, path: str) -> Prompt:
        """
        Reads and parses a YAML prompt file from the given path.

        ## Expected YAML Format:

        ```
        version: <int>  # The version number of the prompt file.

        config:         # Configuration settings for the LLM model (optional).
          model: <str>  # The name or ID of the language model to be used.
          temperature: <float>  # The temperature setting for controlling randomness.
          max_tokens: <int>  # The maximum number of tokens for the model's response.

        messages:       # List of messages to be used in the prompt (required).
        - role: <str>  # The role of the message sender, e.g., 'system', 'user', or 'assistant'.
          content: <str>  # The content of the message.
        ```

        ### Example:

        ```
        version: 0
        config:
          model: gpt-4o-mini
          temperature: 0.0
          max_tokens: 512
        messages:
        - role: system
          content: "You are an assistant that provides helpful responses."
        - role: user
          content: "What is the capital of France?"
        ```
        """
        try:
            prompt_spec = read_yaml(path)
        except Exception as e:
            raise PromptReadError(f"Error reading prompt file ({path}): {e}")

        # Ensure that the prompt file contains the required keys.
        required_keys = ["messages"]

        for key in required_keys:
            if key not in prompt_spec:
                raise PromptReadError(f"Missing key `{key}` in prompt file ({path})")

        messages = [ChatMessage(**msg) for msg in prompt_spec["messages"]]

        return Prompt(
            name=prompt_name,
            parameters=prompt_spec.get("config", {}),
            messages=messages,
        )

    def _load_prompt_map(self, prompts_dir: str) -> dict[str, Prompt]:
        """
        Load prompt names and prompt specs from YAML files in the given directory.

        Args:
            prompts_dir (str): The root directory containing prompt files.

        Returns:
            dict[str, PromptSet]: A dictionary where keys are prompt names (without extensions)
                            and values are PromptSet objects.
        """
        prompt_map = {}
        for path in Path(prompts_dir).rglob("*.yaml"):
            prompt_name = path.stem
            prompt_path = str(path.resolve())
            prompt_map[prompt_name] = self._load_prompt(prompt_name, prompt_path)
        return prompt_map
