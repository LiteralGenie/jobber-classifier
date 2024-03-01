import sys
from pathlib import Path

# Add src/ to PATH
sys.path.append(str(Path(__file__).parent.parent))

import tomli
import uvicorn
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

from config import paths
from db import init_db


def get_db():
    with open(paths.CONFIG_DIR / "config.toml", "rb") as file:
        config = tomli.load(file)

    return init_db(config["db_file"])


app = FastAPI()


class NewPost(BaseModel):
    company: str
    text: str
    title: str

    source: str
    url: str

    time_created: float


@app.post("/create")
def create(post: NewPost):
    try:
        db = get_db()
        db.execute(
            """
            INSERT INTO posts
                ( company,  text,  title,  source,  url,  time_created) VALUES
                (:company, :text, :title, :source, :url, :time_created)
            """,
            dict(post),
        )
        db.commit()
        return Response(status_code=200)
    except Exception as e:
        print(e)
        return Response(content=str(e), status_code=400)


@app.post("/check")
async def check_exists(request: Request):
    db = get_db()
    url = (await request.body()).decode("utf-8")
    return dict(
        exists=bool(db.execute("SELECT id FROM posts WHERE url = ?", [url]).fetchone())
    )


if __name__ == "__main__":
    uvicorn.run("bin._run_server:app", host="0.0.0.0", workers=1, reload=True)
