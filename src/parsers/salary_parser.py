from guidance import gen
from guidance.models import Model

from .parser import Parser


class SalaryParser(Parser[int]):
    def create_prompt(self):
        prompt = "What is the minimum starting salary for this job? Answer with 0 if this information is not available. Do not include any dollar signs ($) or commas (,). Use only numbers."

        prompt += "\nSalary: " + gen(regex=r"\d+", name="salary")  # type: ignore

        return prompt

    def extract_answer(self, output: Model) -> int:
        return int(output["salary"])  # type: ignore
