import yaml


def read_yaml(path: str, encoding: str = "utf-8") -> dict:
    with open(path, encoding=encoding) as f:
        return yaml.safe_load(f)
