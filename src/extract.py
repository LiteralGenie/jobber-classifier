from typing import TypedDict

from guidance import models

from parsers.clearance_parser import ClearanceParser
from parsers.duty_parser import DutyParser
from parsers.salary_parser import SalaryParser
from parsers.skill_parser import SkillParser


class JobData(TypedDict):
    skills: list[str]
    duties: list[str]
    salary: int
    clearance: bool


def extract(
    llm: models.Model,
    description: str,
    skills: list[str],
    duties: list[str],
) -> JobData:
    parsers = dict(
        skills=SkillParser(skills),
        duties=DutyParser(duties),
        salary=SalaryParser(),
        clearance=ClearanceParser(),
    )

    prompt = f"""
Given the job description below, answer the questions that follow it.

Description:
{description}
""".strip()

    for p in parsers.values():
        prompt += f"\n\n{p.create_prompt()}"

    output = llm + prompt

    answers: JobData = {name: p.extract_answer(output) for name, p in parsers.items()}  # type: ignore

    return answers
