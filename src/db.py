import sqlite3


def init_db(fp: str) -> sqlite3.Connection:
    db = sqlite3.connect(fp)
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS indeed_posts (
            id              TEXT        NOT NULL,

            company         TEXT        NOT NULL,
            text            TEXT        NOT NULL,
            title           TEXT        NOT NULL,

            details_html    TEXT        NOT NULL,
            preview_html    TEXT        NOT NULL,

            time_created    REAL        NOT NULL,

            PRIMARY KEY (id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS skills (
            id      INTEGER     PRIMARY KEY,
            name    TEXT        NOT NULL,
            patts   JSON        NOT NULL
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS duties (
            id          INTEGER     PRIMARY KEY,
            name        TEXT        NOT NULL,
            prompt      TEXT        NOT NULL
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS locations (
            id          INTEGER     PRIMARY KEY,

            country     TEXT,
            state       TEXT,
            city        TEXT,

            UNIQUE (country, state, city) ON CONFLICT IGNORE
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS indeed_label_statuses (
            id_post         TEXT        NOT NULL,

            has_skills      BOOLEAN     NOT NULL,
            has_duties      BOOLEAN     NOT NULL,
            has_misc        BOOLEAN     NOT NULL,
            has_locations   BOOLEAN     NOT NULL,
            has_yoe         BOOLEAN     NOT NULL,

            PRIMARY KEY (id_post),
            FOREIGN KEY (id_post) REFERENCES indeed_posts(id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS indeed_skill_labels (
            id_skill    INTEGER     NOT NULL,
            id_post     TEXT        NOT NULL,

            label       BOOLEAN     NOT NULL,

            PRIMARY KEY (id_skill, id_post),
            FOREIGN KEY (id_post) REFERENCES indeed_posts(id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS indeed_duty_labels (
            id_duty     INTEGER     NOT NULL,
            id_post     TEXT        NOT NULL,

            label       BOOLEAN     NOT NULL,

            PRIMARY KEY (id_duty, id_post),
            FOREIGN KEY (id_post) REFERENCES indeed_posts(id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS indeed_misc_labels (
            id_post         TEXT        NOT NULL,

            is_hybrid       BOOLEAN     NOT NULL,
            is_onsite       BOOLEAN     NOT NULL,
            is_remote       BOOLEAN     NOT NULL,
            salary          REAL        NOT NULL,
            clearance       BOOLEAN     NOT NULL,

            PRIMARY KEY (id_post),
            FOREIGN KEY (id_post) REFERENCES indeed_posts(id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS indeed_location_labels (
            id_post         TEXT        NOT NULL,
            id_location     INTEGER     NOT NULL,

            PRIMARY KEY (id_post, id_location),
            FOREIGN KEY (id_post) REFERENCES indeed_posts(id),
            FOREIGN KEY (id_location) REFERENCES locations(id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS indeed_yoe_labels (
            id_post         TEXT        NOT NULL,
            yoe             INTEGER,

            PRIMARY KEY (id_post),
            FOREIGN KEY (id_post) REFERENCES indeed_posts(id)
        )
        """
    )

    return db
