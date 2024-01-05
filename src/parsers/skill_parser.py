from guidance import select
from guidance.models import Model

from .parser import Parser


class SkillParser(Parser[bool]):
    def __init__(self, skill: str):
        self.skill = skill

    def create_prompt(self):
        prompt = f"Is working with {self.skill} part of this job's responsibilities / duties? Ignore the requirements section. Answer with a yes or no."
        prompt += "\nAnswer: " + select(["yes", "no"], name=self.skill)
        return prompt

    def extract_answer(self, output: Model) -> bool:
        return output[self.skill] == "yes"
