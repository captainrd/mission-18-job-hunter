import unittest

import yaml

from core.filter import JobFilter, extract_experience
from core.models import Job


def make_job(
    title: str = "Business Analyst",
    location: str = "Mumbai, India",
    description: str = "Requires 3-5 years of experience",
) -> Job:
    return Job(
        job_id="1",
        title=title,
        company="Example Bank",
        location=location,
        url="https://example.com/1",
        posted_date="",
        description=description,
    )


class FilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open("config/roles.yaml", encoding="utf-8") as handle:
            cls.job_filter = JobFilter(yaml.safe_load(handle))

    def test_extracts_experience_range(self) -> None:
        self.assertEqual(extract_experience("Requires 2 to 6 years"), (2, 6))
        self.assertEqual(extract_experience("Minimum 4+ yrs"), (4, 4))

    def test_accepts_target_job(self) -> None:
        result = self.job_filter.evaluate(make_job())
        self.assertTrue(result.accepted)
        self.assertEqual(result.experience, (3, 5))

    def test_accepts_missing_experience(self) -> None:
        result = self.job_filter.evaluate(make_job(description="SQL and agile"))
        self.assertTrue(result.accepted)
        self.assertIsNone(result.experience)

    def test_rejects_excluded_seniority(self) -> None:
        result = self.job_filter.evaluate(
            make_job(title="Director, Business Analyst")
        )
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "excluded_seniority")

    def test_rejects_location(self) -> None:
        result = self.job_filter.evaluate(make_job(location="London, UK"))
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "location_not_targeted")

    def test_rejects_high_experience(self) -> None:
        result = self.job_filter.evaluate(
            make_job(description="Requires 10+ years of experience")
        )
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "experience_too_high")


if __name__ == "__main__":
    unittest.main()

