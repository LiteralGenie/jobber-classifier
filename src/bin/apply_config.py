import sys
from pathlib import Path

# Add src/ to PATH
sys.path.append(str(Path(__file__).parent.parent))

import json

import tomli

from config import paths
from db import init_db


def diff_skills(db, config):
    fromDb = [
        dict(r) for r in db.execute("SELECT id, name, patts FROM skills").fetchall()
    ]

    # Find new skills
    dbNames = [sk["name"] for sk in fromDb]
    toCreate = [sk for sk in config["skills"] if sk["name"] not in dbNames]

    # Find deleted skills
    configNames = [sk["name"] for sk in config["skills"]]
    toDelete = [sk for sk in fromDb if sk["name"] not in configNames]

    return dict(toCreate=toCreate, toDelete=toDelete)


def diff_duties(db, config):
    fromDb = [
        dict(r) for r in db.execute("SELECT id, name, prompt FROM duties").fetchall()
    ]

    # Find new duties
    dbNames = [dt["name"] for dt in fromDb]
    toCreate = [dt for dt in config["duties"] if dt["name"] not in dbNames]

    # Find deleted duties
    configNames = [dt["name"] for dt in config["duties"]]
    toDelete = [dt for dt in fromDb if dt["name"] not in configNames]

    return dict(toCreate=toCreate, toDelete=toDelete)


def print_db(db):
    skills = [r["name"] for r in db.execute("SELECT name FROM skills").fetchall()]
    print("Current skills in database: ", ", ".join(skills))

    duties = [r["name"] for r in db.execute("SELECT name FROM duties").fetchall()]
    print("Current duties in database: ", ", ".join(duties))


if __name__ == "__main__":
    with open(paths.CONFIG_DIR / "config.toml", "rb") as file:
        config = tomli.load(file)

    db = init_db(config["db_file"])

    skill_changes = diff_skills(db, config)
    duty_changes = diff_duties(db, config)

    # Early return if no changes
    if (
        not skill_changes["toCreate"]
        and not skill_changes["toDelete"]
        and not duty_changes["toCreate"]
        and not duty_changes["toDelete"]
    ):
        print(
            f"""
No changes to the config\'s skills and duties sections detected.
To configure skills / duties already in the database, please try editing the database directly.
The database is located at {Path(config['db_file']).absolute()}
            """.strip()
        )
        print()
        print_db(db)
        sys.exit()

    # Prompt user to confirm changes
    if skill_changes["toCreate"]:
        print(
            f'Inserting {len(skill_changes["toCreate"])} new skills: {skill_changes["toCreate"]}'
        )
    if skill_changes["toDelete"]:
        print(
            f'Deleting labels for {len(skill_changes["toDelete"])} skills: {skill_changes["toDelete"]}'
        )
    if duty_changes["toCreate"]:
        print(
            f'Inserting {len(duty_changes["toCreate"])} new duties: {duty_changes["toCreate"]}'
        )
    if duty_changes["toDelete"]:
        print(
            f'Deleting labels for {len(duty_changes["toDelete"])} duties: {duty_changes["toDelete"]}'
        )

    confirmation = ""
    while not confirmation.strip().startswith("y"):
        confirmation = input("Please enter 'y' to confirm the above changes: ")

    # Apply changes
    if skill_changes["toCreate"]:
        db.executemany(
            "INSERT INTO skills (name, patts) VALUES (?, ?)",
            [[sk["name"], json.dumps(sk["patts"])] for sk in skill_changes["toCreate"]],
        )
        db.execute("UPDATE label_statuses SET has_skills = 0")

    if skill_changes["toDelete"]:
        db.executemany(
            "DELETE FROM skills WHERE name = ?",
            [sk["name"] for sk in skill_changes["toDelete"]],
        )
        db.execute("UPDATE label_statuses SET has_skills = 0")

    if duty_changes["toCreate"]:
        db.executemany(
            "INSERT INTO duties (name, prompt) VALUES (?, ?)",
            [[dt["name"], dt["prompt"]] for dt in duty_changes["toCreate"]],
        )
        db.execute("UPDATE label_statuses SET has_duties = 0")

    if duty_changes["toDelete"]:
        db.executemany(
            "DELETE FROM duties WHERE name = ?",
            [[dt["name"]] for dt in duty_changes["toDelete"]],
        )
        db.execute("UPDATE label_statuses SET has_duties = 0")

    # Save and display db content
    db.commit()
    print("\n\nAll done!")
    print_db(db)
