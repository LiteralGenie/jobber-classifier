import sys
from pathlib import Path

# Add src/ to PATH
sys.path.append(str(Path(__file__).parent.parent))

import tomli
from guidance import models

from config import paths
from db import init_db, update_db_duties, update_db_skills
from extract import extract
from parsers.clearance_parser import ClearanceParser
from parsers.duty_parser import DutyParser
from parsers.salary_parser import SalaryParser
from parsers.skill_parser import SkillParser

with open(paths.CONFIG_DIR / "config.toml", "rb") as file:
    config = tomli.load(file)

# Prep db
db = init_db(config["db_file"])
update_db_skills(db, config["skills"])
update_db_duties(db, config["duties"])

# Load model
print("Loading model")
llm = models.LlamaCpp(
    model=config["model_file"],
    n_gpu_layers=9999 if config["use_gpu"] else -1,
    n_ctx=4096,
)

# Label skills
skills = db.execute("SELECT id, name FROM skills").fetchall()
for skill in skills:
    missing = db.execute(
        """
        SELECT post.id, post.text, post.title FROM indeed_posts post
        LEFT JOIN indeed_skill_labels lbl 
            ON lbl.id_post = post.id
            AND lbl.id_skill = ?
        WHERE lbl.id_post IS NULL
        """,
        [skill["id"]],
    ).fetchall()
    print(f"Found {len(missing)} posts missing labels for skill {skill['name']}")

    for post in missing:
        print(f"Checking for [{skill['name']}] in [{post['title']}]")
        label = int(extract(llm, post["text"], SkillParser(skill["name"])))
        db.execute(
            """
            INSERT INTO indeed_skill_labels 
            (id_post, id_skill, label) VALUES
            (?, ?, ?)
            """,
            [post["id"], skill["id"], label],
        )
        db.commit()


# Label duties
duties = db.execute("SELECT id, name, prompt FROM duties").fetchall()
for dt in duties:
    missing = db.execute(
        """
        SELECT post.id, post.text, post.title FROM indeed_posts post
        LEFT JOIN indeed_duty_labels lbl 
            ON lbl.id_post = post.id
            AND lbl.id_duty = ?
        WHERE lbl.id_post IS NULL
        """,
        [dt["id"]],
    ).fetchall()
    print(f"Found {len(missing)} posts missing labels for duty {dt['name']}")

    for post in missing:
        print(f"Checking for [{dt['name']}] in [{post['title']}]")
        label = int(extract(llm, post["text"], DutyParser(dt["prompt"])))
        db.execute(
            """
            INSERT INTO indeed_duty_labels 
            (id_post, id_duty, label) VALUES
            (?, ?, ?)
            """,
            [post["id"], dt["id"], label],
        )
        db.commit()

# Label salary and clearance
missing = db.execute(
    """
    SELECT post.id, post.text, post.title FROM indeed_posts post
    LEFT JOIN indeed_misc_labels lbl
    ON lbl.id_post = post.id
    WHERE lbl.id_post IS NULL
    """
).fetchall()

for post in missing:
    salary = extract(llm, post["text"], SalaryParser())
    clearance = extract(llm, post["text"], ClearanceParser())

    print(f"Checking for misc labels in [{post['title']}]")
    db.execute(
        """
        INSERT INTO indeed_misc_labels 
        (id_post, salary, clearance) VALUES
        (?, ?, ?)
        """,
        [post["id"], salary, clearance],
    )
    db.commit()
