from guidance import select
from guidance.models import Model

from .parser import Parser


class DutyParser(Parser[bool]):
    def __init__(self, prompt: str):
        self.prompt = prompt

    def create_prompt(self):
        prompt = f"{self.prompt} Answer with a yes or no."
        prompt += "\nAnswer: " + select(["yes", "no"], name=self.prompt)
        return prompt

    def extract_answer(self, output: Model) -> bool:
        return output[self.prompt] == "yes"
