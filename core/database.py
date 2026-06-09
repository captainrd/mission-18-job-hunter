import sqlite3
from pathlib import Path

from core.models import Job
from core.normalize import utc_now


class JobDatabase:
    def __init__(self, path: str | Path, schema_path: str | Path) -> None:
        self.path = path
        if str(path) != ":memory:":
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            self.path = file_path
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        schema = Path(schema_path).read_text(encoding="utf-8")
        self.connection.executescript(schema)

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "JobDatabase":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @staticmethod
    def job_key(job: Job) -> str:
        return f"{job.company.casefold()}::{job.job_id}"

    def is_seen(self, job: Job) -> bool:
        row = self.connection.execute(
            "SELECT 1 FROM seen_jobs WHERE job_key = ?", (self.job_key(job),)
        ).fetchone()
        return row is not None

    def save(self, job: Job) -> bool:
        if self.is_seen(job):
            return False
        now = utc_now()
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO jobs (
                    job_id, title, company, location, url, posted_date,
                    score, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.job_id,
                    job.title,
                    job.company,
                    job.location,
                    job.url,
                    job.posted_date,
                    job.score,
                    job.status,
                    now,
                ),
            )
            self.connection.execute(
                "INSERT INTO seen_jobs (job_key, first_seen) VALUES (?, ?)",
                (self.job_key(job), now),
            )
        return True
