import tomli
import uvicorn
from fastapi import FastAPI, HTTPException
from guidance import models
from pydantic import BaseModel

from config import paths
from extract import JobData, extract_llm, extract_regex
from parsers.clearance_parser import ClearanceParser
from parsers.duty_parser import DutyParser
from parsers.salary_parser import SalaryParser

app = FastAPI()

with open(paths.CONFIG_DIR / "config.toml", "rb") as file:
    config = tomli.load(file)


class ParseRequest(BaseModel):
    description: str
    skills: list[str]
    duties: list[str]


def _handle_request(req: ParseRequest, llm: models.Model) -> JobData:
    skills = []
    for id in req.skills:
        try:
            sk = next(sk for sk in config["skills"] if sk["name"] == id)
            is_match = extract_regex(req.description, sk["patts"])
            if is_match:
                skills.append(id)
        except StopIteration:
            raise HTTPException(400, f"Invalid skill id {id}")

    duties = []
    for id in req.duties:
        try:
            dt = next(dt for dt in config["skills"] if dt["name"] == id)
            is_match = extract_llm(llm, req.description, DutyParser(dt["prompt"]))
            if is_match:
                duties.append(id)
        except StopIteration:
            raise HTTPException(400, f"Invalid duty id {id}")

    clearance = extract_llm(llm, req.description, ClearanceParser())

    salary = extract_llm(llm, req.description, SalaryParser())

    return JobData(
        skills=skills,
        duties=duties,
        clearance=clearance,
        salary=salary,
    )


@app.post("/parse")
def parse(reqs: list[ParseRequest]):
    llm = models.LlamaCpp(
        model=config["model_file"],
        n_gpu_layers=999,  # load everything into gpu
        n_ctx=4096,
    )

    result: list[JobData] = []
    for r in reqs:
        result.append(_handle_request(r, llm))

    return result


if __name__ == "__main__":
    uvicorn.run(app, host=config["host"], port=config["port"], workers=1)
