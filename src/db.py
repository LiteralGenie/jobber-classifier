import sqlite3


def init_db(fp: str) -> sqlite3.Connection:
    db = sqlite3.connect(fp)
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id              INTEGER     PRIMARY KEY,

            company         TEXT        NOT NULL,
            text            TEXT        NOT NULL,
            title           TEXT        NOT NULL,
            
            source          TEXT        NOT NULL,
            url             TEXT        NOT NULL,

            time_created    REAL        NOT NULL,

            UNIQUE (url) ON CONFLICT FAIL
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
        CREATE TABLE IF NOT EXISTS label_statuses (
            id_post         INTEGER     NOT NULL,

            has_skills      BOOLEAN     NOT NULL,
            has_duties      BOOLEAN     NOT NULL,
            has_misc        BOOLEAN     NOT NULL,
            has_locations   BOOLEAN     NOT NULL,
            has_yoe         BOOLEAN     NOT NULL,

            PRIMARY KEY (id_post),
            FOREIGN KEY (id_post) REFERENCES posts(id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS skill_labels (
            id_skill    INTEGER     NOT NULL,
            id_post     INTEGER     NOT NULL,

            label       BOOLEAN     NOT NULL,

            PRIMARY KEY (id_skill, id_post),
            FOREIGN KEY (id_post) REFERENCES posts(id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS duty_labels (
            id_duty     INTEGER     NOT NULL,
            id_post     INTEGER     NOT NULL,

            label       BOOLEAN     NOT NULL,

            PRIMARY KEY (id_duty, id_post),
            FOREIGN KEY (id_post) REFERENCES posts(id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS misc_labels (
            id_post         INTEGER     NOT NULL,

            is_hybrid       BOOLEAN     NOT NULL,
            is_onsite       BOOLEAN     NOT NULL,
            is_remote       BOOLEAN     NOT NULL,
            salary          REAL,
            clearance       BOOLEAN     NOT NULL,

            PRIMARY KEY (id_post),
            FOREIGN KEY (id_post) REFERENCES posts(id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS location_labels (
            id_post         INTEGER     NOT NULL,
            id_location     INTEGER     NOT NULL,

            PRIMARY KEY (id_post, id_location),
            FOREIGN KEY (id_post) REFERENCES posts(id),
            FOREIGN KEY (id_location) REFERENCES locations(id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS yoe_labels (
            id_post         INTEGER     NOT NULL,
            yoe             INTEGER,

            PRIMARY KEY (id_post),
            FOREIGN KEY (id_post) REFERENCES posts(id)
        )
        """
    )

    return db
