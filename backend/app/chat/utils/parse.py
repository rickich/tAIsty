import json
import re

from app.chat.utils.constants import USER_INFO


def parse_function_calls(text: str):
    # 모든 function call을 찾는 정규 표현식
    function_pattern = r"<function=.*?</function>"
    function_matches = re.findall(function_pattern, text)

    parsed_calls = {}

    for function_call_string in function_matches:
        # 각 function call을 파싱
        parse_pattern = r"<function=(\w+)&(.*?)></function>"
        match = re.match(parse_pattern, function_call_string)

        if match:
            args_string = match.group(2)

            # 인자를 파싱
            args_dict = {}
            for arg in args_string.split("&"):
                key, value = arg.split("=")
                try:
                    # JSON 형식으로 파싱 시도
                    args_dict[key] = json.loads(value)
                except json.JSONDecodeError:
                    # JSON 파싱에 실패하면 문자열 그대로 사용
                    args_dict[key] = value.strip('"')

            preference_key = args_dict["preference_type"]
            selected_preferences = []
            if preference_key in USER_INFO:
                for p in args_dict["selected_preferences"]:
                    if p in USER_INFO[preference_key]:
                        selected_preferences.append(p)
                parsed_calls[preference_key] = selected_preferences

    return parsed_calls


def parse_remove_function_calls(text):
    function_pattern = r"<function=(.*?)</function>"
    function_matches = re.findall(function_pattern, text)

    parsed_calls = {}

    for function_call_string in function_matches:
        args_dict = {}
        for arg in function_call_string.split("&"):
            if "=" in arg:
                key, value = arg.split("=", 1)
                try:
                    args_dict[key] = json.loads(value)
                except json.JSONDecodeError:
                    args_dict[key] = value.strip('"')

        preference_type = args_dict.get("preference_type")
        selected_preferences = args_dict.get("selected_preferences", [])

        if preference_type:
            if preference_type not in parsed_calls:
                parsed_calls[preference_type] = []
            parsed_calls[preference_type].extend(selected_preferences)

    return parsed_calls


def parse_preferences_or_restrictions(conditions: dict):
    return f"{', '.join([f"{k.replace('_', ' ')}: {', '.join(v) if isinstance(v, list) else v}" for k, v in conditions.items()])}"


def parse_additional_preferences(conditions: dict):
    all_condition_set = set(USER_INFO.keys())
    except_keys = all_condition_set - set(conditions.keys())

    return f"{', '.join([k.replace('_', ' ') for k in except_keys if k not in conditions])}"
