from guidance import select
from guidance.models import Model

from .parser import Parser


class DutyParser(Parser[list[str]]):
    def __init__(self, questions: list[str]):
        self.questions = questions

    def create_prompt(self):
        qs = []

        for q in self.questions:
            prompt = f"{q} Answer with a yes or no."
            prompt += "\nAnswer: " + select(["yes", "no"], name=q)
            qs.append(prompt)

        prompt = qs[0]
        for q in qs[1:]:
            prompt += "\n\n" + q

        return prompt

    def extract_answer(self, output: Model) -> list[str]:
        return [q for q in self.questions if output[q] == "yes"]
