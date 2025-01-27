from pydantic import BaseModel


class BaseArgs(BaseModel):
    id: str


class BaseAgent:
    def __init__(self):
        pass

    def run(self, args: BaseArgs):
        pass
