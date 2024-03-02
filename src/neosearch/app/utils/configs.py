import yaml

# custom imports
from neosearch.utils.singleton import Singleton


def get_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


class Config(metaclass=Singleton):
    def __init__(self):
        self.config = get_config()

    def get(self, key):
        return self.config.get(key)

    def get_llm_configs(self):
        llm_config = self.config.get("neosearch", {}).get("llm", {})
        return llm_config
