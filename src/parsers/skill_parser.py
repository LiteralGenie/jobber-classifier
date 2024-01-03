from guidance import select
from guidance.models import Model

from .parser import Parser


class SkillParser(Parser[list[str]]):
    def __init__(self, skills: list[str]):
        self.skills = skills

    def create_prompt(self):
        prompt = "Which technologies are part of the job responsibilities / duties? For each technology, answer with a yes or no."

        for sk in self.skills:
            prompt += f"\n{sk}: " + select(["yes", "no"], name=sk)

        return prompt

    def extract_answer(self, output: Model) -> list[str]:
        return [sk for sk in self.skills if output[sk] == "yes"]
