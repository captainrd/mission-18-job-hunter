import tempfile
import unittest
from pathlib import Path

from core.database import JobDatabase
from core.models import Job


class DatabaseTests(unittest.TestCase):
    def test_supports_in_memory_database(self) -> None:
        with JobDatabase(":memory:", "database/schema.sql") as database:
            count = database.connection.execute(
                "SELECT COUNT(*) FROM jobs"
            ).fetchone()[0]
            self.assertEqual(count, 0)

    def test_save_deduplicates_company_and_job_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "jobs.db"
            with JobDatabase(database_path, "database/schema.sql") as database:
                job = Job(
                    job_id="REQ-1",
                    title="Risk Analyst",
                    company="Example Bank",
                    location="Pune",
                    url="https://example.com/1",
                    posted_date="2026-06-10",
                    score=90,
                )
                self.assertTrue(database.save(job))
                self.assertFalse(database.save(job))
                count = database.connection.execute(
                    "SELECT COUNT(*) FROM jobs"
                ).fetchone()[0]
                self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
