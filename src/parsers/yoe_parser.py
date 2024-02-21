from typing import TypeAlias

from guidance import regex, select
from guidance.models import Model

from .parser import Parser

NULL_ANSWER = "null"

YoeAnswer: TypeAlias = int | None


class YoeParser(Parser[list[YoeAnswer]]):
    def create_prompt(self):
        prompt = f"""
What is the minimum number of years of experience necessary for this position?
Write '{NULL_ANSWER}' if this information is not provided.
""".strip()
        prompt += "\n\nAnswer: " + select([regex(r"\d+"), NULL_ANSWER], name="yoe")  # type: ignore
        return prompt

    def extract_answer(self, output: Model) -> YoeAnswer:
        answer: str = output["yoe"]  # type: ignore

        if answer == NULL_ANSWER:
            return None

        return int(answer)
