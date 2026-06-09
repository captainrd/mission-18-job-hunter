import unittest

import yaml

from core.models import Job
from core.score import JobScorer


class ScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open("config/roles.yaml", encoding="utf-8") as handle:
            roles = yaml.safe_load(handle)
        with open("config/scoring.yaml", encoding="utf-8") as handle:
            scoring = yaml.safe_load(handle)
        cls.scorer = JobScorer(scoring, roles)

    def test_scores_ideal_job_at_100(self) -> None:
        job = Job(
            job_id="42",
            title="Business Analyst",
            company="Example Bank",
            company_domain="banking",
            location="Mumbai, India",
            url="https://example.com/42",
            posted_date="",
            description="MBA preferred. Requires 4 years of experience.",
        )
        self.scorer.score(job)
        self.assertEqual(job.score, 100)
        self.assertEqual(job.score_breakdown["experience_match"], 20)

    def test_missing_experience_does_not_receive_experience_points(self) -> None:
        job = Job(
            job_id="43",
            title="Product Analyst",
            company="Example",
            company_domain="product",
            location="Remote",
            url="https://example.com/43",
            posted_date="",
            description="Work with stakeholders",
        )
        self.scorer.score(job)
        self.assertEqual(job.score, 80)
        self.assertEqual(job.score_breakdown["experience_match"], 0)


if __name__ == "__main__":
    unittest.main()

