from guidance import select
from guidance.models import Model

from .parser import Parser


class ClearanceParser(Parser[bool]):
    def create_prompt(self):
        prompt = (
            "Is a security clearance required for this job? Answer with a yes or no."
        )

        prompt += "\nClearance: " + select(["yes", "no"])  # type: ignore

        return prompt

    def extract_answer(self, output: Model) -> bool:
        return output["clearance"] == "yes"
