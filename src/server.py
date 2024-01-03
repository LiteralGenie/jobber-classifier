import tomli
import uvicorn
from fastapi import FastAPI
from guidance import models
from pydantic import BaseModel

from config import paths
from extract import JobData, extract

app = FastAPI()

with open(paths.CONFIG_DIR / "config.toml", "rb") as file:
    config = tomli.load(file)


class ParseRequest(BaseModel):
    description: str
    skills: list[str]
    duties: list[str]


@app.post("/parse")
def parse(reqs: list[ParseRequest]):
    llm = models.LlamaCpp(
        model=config["model_file"],
        n_gpu_layers=999,  # load everything into gpu
        n_ctx=4096,
    )

    result: list[JobData] = []
    for r in reqs:
        data = extract(
            llm,
            description=r.description,
            skills=r.skills,
            duties=r.duties,
        )
        result.append(data)

    return result


if __name__ == "__main__":
    uvicorn.run(app, host=config["host"], port=config["port"], workers=1)
