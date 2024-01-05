from typing import TypedDict, TypeVar

from guidance import models

from parsers.parser import Parser

T = TypeVar("T")


class JobData(TypedDict):
    skills: list[str]
    duties: list[str]
    salary: int
    clearance: bool


def extract(llm: models.Model, description: str, parser: Parser[T]) -> T:
    prompt = "A job description is listed below. Answer the question that follows it."
    prompt += "\n\n" + f"Job Description:\n{description}"
    prompt += "\n\n" + parser.create_prompt()

    output = llm + prompt
    answer = parser.extract_answer(output)
    return answer


# def extract(
#     llm: models.Model,
#     description: str,
#     skills: list[str],
#     duties: list[str],
# ) -> JobData:
#     get = lambda parser: _extract(llm, description, parser)

#     return JobData(
#         skills={sk: get(SkillParser(sk)) for sk in skills},  # type: ignore
#         duties={d: get(DutyParser(d)) for d in duties},  # type: ignore
#         salary=get(SalaryParser()),
#         clearance=get(ClearanceParser()),
#     )
