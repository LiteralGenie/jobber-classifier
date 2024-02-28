import sys
from pathlib import Path

# Add src/ to PATH
sys.path.append(str(Path(__file__).parent.parent))

import json

import tomli
from guidance import models
from tqdm import tqdm

from config import paths
from db import init_db, update_db_duties, update_db_skills
from extract import extract_llm, extract_regex
from parsers.clearance_parser import ClearanceParser
from parsers.duty_parser import DutyParser
from parsers.location_parser import LocationParser
from parsers.location_type_parser import HybridParser, OnsiteParser, RemoteParser
from parsers.salary_parser import SalaryParser
from parsers.yoe_parser import YoeParser

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
    n_ctx=8192,
    echo=False,
)

# Read globals
skills = db.execute("SELECT id, name, patts FROM skills").fetchall()
duties = db.execute("SELECT id, name, prompt FROM duties").fetchall()

# Filter posts with missing labels
missing = db.execute(
    """
    SELECT
        post.id,
        post.title,
        post.text,
        status.id_post AS id_status,
        status.has_skills,
        status.has_duties,
        status.has_misc,
        status.has_locations,
        status.has_yoe
    FROM indeed_posts post
    LEFT JOIN indeed_label_statuses status
        ON post.id = status.id_post
    WHERE (
        COALESCE(status.has_skills, 0) = 0
        OR COALESCE(status.has_duties, 0) = 0
        OR COALESCE(status.has_misc, 0) = 0
        OR COALESCE(status.has_locations, 0) = 0
        OR COALESCE(status.has_yoe, 0) = 0
    )
    ORDER BY post.rowid ASC
    """
).fetchall()

for post in (pbar := tqdm(missing)):
    pbar.set_description(f"Labeling [{post['title']}]")
    pbar.refresh()

    if post["id_status"] is None:
        db.execute(
            """
            INSERT INTO indeed_label_statuses
            (id_post, has_skills, has_duties, has_misc, has_locations) VALUES
            (?, ?, ?, ?, ?)
            """,
            [post["id"], 0, 0, 0, 0],
        )
        db.commit()

    # Label skills
    if not post["has_skills"]:
        rows = []
        for skill in skills:
            patts = json.loads(skill["patts"])
            label = int(extract_regex(post["text"], patts))
            rows.append(
                dict(
                    id_post=post["id"],
                    id_skill=skill["id"],
                    label=label,
                )
            )

        db.executemany(
            """
            INSERT INTO indeed_skill_labels 
            ( id_post,  id_skill,  label) VALUES
            (:id_post, :id_skill, :label)
            """,
            rows,
        )
        db.execute(
            """
            UPDATE indeed_label_statuses
            SET has_skills = ?
            WHERE id_post = ?
            """,
            [1, post["id"]],
        )
        db.commit()

    # Label duties
    if not post["has_duties"]:
        rows = []
        for dt in duties:
            label = int(extract_llm(llm, post["text"], DutyParser(dt["prompt"])))
            rows.append(
                dict(
                    id_post=post["id"],
                    id_duty=dt["id"],
                    label=label,
                )
            )

        db.executemany(
            """
            INSERT INTO indeed_duty_labels 
            ( id_post,  id_duty,  label) VALUES
            (:id_post, :id_duty, :label)
            """,
            rows,
        )
        db.execute(
            """
            UPDATE indeed_label_statuses
            SET has_duties = ?
            WHERE id_post = ?
            """,
            [1, post["id"]],
        )
        db.commit()

    # Label misc
    if not post["has_misc"]:
        salary = extract_llm(llm, post["text"], SalaryParser())
        clearance = extract_llm(llm, post["text"], ClearanceParser())

        is_hybrid = extract_llm(llm, post["text"], HybridParser())
        is_onsite = extract_llm(llm, post["text"], OnsiteParser())
        is_remote = extract_llm(llm, post["text"], RemoteParser())

        db.execute(
            """
            INSERT INTO indeed_misc_labels 
            (id_post, salary, clearance, is_hybrid, is_onsite, is_remote) VALUES
            (?, ?, ?, ?, ?, ?)
            """,
            [post["id"], salary, clearance, is_hybrid, is_onsite, is_remote],
        )
        db.execute(
            """
            UPDATE indeed_label_statuses
            SET has_misc = ?
            WHERE id_post = ?
            """,
            [1, post["id"]],
        )
        db.commit()

    # Label locations
    if not post["has_locations"]:
        locations = extract_llm(llm, post["text"], LocationParser())

        db.executemany(
            """
            INSERT OR IGNORE INTO locations
            ( country,  state,  city) VALUES
            (:country, :state, :city)
            """,
            locations,
        )
        db.commit()

        rows = []
        for loc in locations:
            check = lambda key, val: (
                f"{key} = :{key}" if val is not None else f"{key} IS NULL"
            )

            r = db.execute(
                f"""
                SELECT id FROM locations
                WHERE
                    {check('country', loc['country'])}
                    AND {check('state', loc['state'])}
                    AND {check('city', loc['city'])}
                """,
                loc,
            ).fetchone()

            rows.append(
                dict(
                    id_post=post["id"],
                    id_location=r["id"],
                )
            )

        # Need OR IGNORE bc normalization step in parser can technically cause dupes
        db.executemany(
            """
            INSERT OR IGNORE INTO indeed_location_labels
            ( id_post,  id_location) VALUES
            (:id_post, :id_location)
            """,
            rows,
        )
        db.execute(
            """
            UPDATE indeed_label_statuses
            SET has_locations = ?
            WHERE id_post = ?
            """,
            [1, post["id"]],
        )
        db.commit()

    # Label YoE
    if not post["has_yoe"]:
        yoe = extract_llm(llm, post["text"], YoeParser())

        db.execute(
            """
            INSERT INTO indeed_yoe_labels 
            (id_post, yoe) VALUES
            (?, ?)
            """,
            [post["id"], yoe],
        )
        db.execute(
            """
            UPDATE indeed_label_statuses
            SET has_yoe = ?
            WHERE id_post = ?
            """,
            [1, post["id"]],
        )
        db.commit()
