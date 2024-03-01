import re
from typing import TypedDict, TypeVar

from guidance import models

from parsers.parser import Parser

T = TypeVar("T")


class JobData(TypedDict):
    skills: list[str]
    duties: list[str]
    salary: int
    clearance: bool


def extract_llm(llm: models.Model, description: str, parser: Parser[T]) -> T:
    prompt = "A job description is listed below. Answer the question that follows it."
    prompt += "\n\n" + f"Job Description:\n{description}"
    prompt += "\n\n" + parser.create_prompt()

    output = llm + prompt
    answer = parser.extract_answer(output)
    return answer


def extract_regex(description: str, patts: list[str]) -> bool:
    for p in patts:
        m = re.search(p, description, flags=re.IGNORECASE)
        if m:
            return True
    else:
        return False
