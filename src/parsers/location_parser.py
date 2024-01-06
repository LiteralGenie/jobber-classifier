from guidance import select
from guidance.models import Model

from .parser import Parser


class HybridParser(Parser[bool]):
    def create_prompt(self):
        prompt = "Does this position allow a hybrid attendance schedule? Answer with yes or no."

        prompt += "\nAnswer: " + select(["yes", "no"], name="hybrid")  # type: ignore

        return prompt

    def extract_answer(self, output: Model) -> bool:
        return output["hybrid"] == "yes"


class RemoteParser(Parser[bool]):
    def create_prompt(self):
        prompt = "Does this position allow fully remote work? Answer with yes or no."

        prompt += "\nAnswer: " + select(["yes", "no"], name="remote")  # type: ignore

        return prompt

    def extract_answer(self, output: Model) -> bool:
        return output["remote"] == "yes"
