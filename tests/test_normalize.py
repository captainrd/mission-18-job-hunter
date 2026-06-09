import unittest

from core.models import RawJob
from core.normalize import normalize_job


class NormalizeTests(unittest.TestCase):
    def test_normalizes_html_and_generates_stable_id(self) -> None:
        raw = RawJob(
            title=" Business&nbsp;Analyst ",
            location="<b>Mumbai</b>",
            url="https://example.com/jobs/1",
            description="<p>Requires SQL</p>",
        )
        company = {"name": "Example Bank", "domain": "banking"}

        first = normalize_job(raw, company)
        second = normalize_job(raw, company)

        self.assertEqual(first.title, "Business Analyst")
        self.assertEqual(first.location, "Mumbai")
        self.assertEqual(first.description, "Requires SQL")
        self.assertEqual(first.job_id, second.job_id)
        self.assertEqual(len(first.job_id), 24)

    def test_preserves_external_id(self) -> None:
        raw = RawJob(
            external_id="REQ-42",
            title="Product Analyst",
            location="Pune",
            url="https://example.com/42",
        )
        job = normalize_job(raw, {"name": "Example", "domain": "product"})
        self.assertEqual(job.job_id, "REQ-42")


if __name__ == "__main__":
    unittest.main()

