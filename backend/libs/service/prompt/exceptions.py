from core.exceptions.base import CustomException


class PromptCompileError(CustomException):
    code = 500
    error_code = "PROMPT_COMPILE_ERROR"
    message = "Error compiling prompt"


class PromptReadError(CustomException):
    code = 500
    error_code = "PROMPT_READ_ERROR"
    message = "Error reading prompt file"


class PromptNotFoundError(CustomException):
    code = 500
    error_code = "PROMPT_NOT_FOUND"
    message = "Prompt not found"
