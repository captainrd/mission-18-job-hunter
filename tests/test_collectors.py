import unittest

from collectors.greenhouse import GreenhouseCollector
from collectors.oracle import OracleCollector
from collectors.smartrecruiters import SmartRecruitersCollector
from collectors.workday import WorkdayCollector


class FakeClient:
    def get_json(self, url: str, **kwargs: object) -> dict[str, object]:
        return {
            "jobs": [
                {
                    "id": 123,
                    "title": "Business Analyst",
                    "location": {"name": "Mumbai"},
                    "absolute_url": "https://example.com/123",
                    "updated_at": "2026-06-10T01:00:00Z",
                    "content": "<p>3 years</p>",
                }
            ]
        }

    def post_json(self, url: str, **kwargs: object) -> dict[str, object]:
        return {
            "total": 1,
            "jobPostings": [
                {
                    "title": "Risk Analyst",
                    "locationsText": "Pune",
                    "externalPath": "/job/Pune/Risk-Analyst_REQ-9",
                    "bulletFields": ["REQ-9"],
                    "postedOn": "Posted Today",
                }
            ],
        }


class OracleFakeClient:
    def get_json(self, url: str, **kwargs: object) -> dict[str, object]:
        return {
            "items": [
                {
                    "TotalJobsCount": 1,
                    "requisitionList": [
                        {
                            "Id": "210",
                            "Title": "Business Analyst",
                            "PrimaryLocation": "Mumbai, Maharashtra, India",
                            "PostedDate": "2026-06-10",
                            "ShortDescriptionStr": "Requires 4 years experience",
                        }
                    ],
                }
            ]
        }


class SmartRecruitersFakeClient:
    def get_json(self, url: str, **kwargs: object) -> dict[str, object]:
        return {
            "totalFound": 1,
            "content": [
                {
                    "id": "744",
                    "name": "Product Analyst",
                    "releasedDate": "2026-06-10T01:00:00Z",
                    "location": {"fullLocation": "Hyderabad, India"},
                }
            ],
        }


class CollectorTests(unittest.TestCase):
    def test_greenhouse_mapping(self) -> None:
        jobs = GreenhouseCollector(FakeClient()).collect(
            {"name": "Example", "board_token": "example"}
        )
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].external_id, "123")
        self.assertEqual(jobs[0].location, "Mumbai")

    def test_workday_mapping(self) -> None:
        jobs = WorkdayCollector(FakeClient()).collect(
            {
                "name": "Example",
                "base_url": "https://example.wd5.myworkdayjobs.com",
                "tenant": "example",
                "site": "External",
            }
        )
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].external_id, "REQ-9")
        self.assertIn("External/job/Pune", jobs[0].url)

    def test_oracle_candidate_experience_mapping(self) -> None:
        jobs = OracleCollector(OracleFakeClient()).collect(
            {
                "name": "Example",
                "api_url": "https://example.com/recruitingCEJobRequisitions",
                "site_number": "CX_1",
                "career_url": "https://example.com/sites/CX_1/job",
                "search_location": "India",
                "search_keywords": ["Business Analyst"],
            }
        )
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].external_id, "210")
        self.assertEqual(jobs[0].location, "Mumbai, Maharashtra, India")
        self.assertEqual(jobs[0].url, "https://example.com/sites/CX_1/job/210")

    def test_smartrecruiters_builds_public_posting_url(self) -> None:
        jobs = SmartRecruitersCollector(SmartRecruitersFakeClient()).collect(
            {"name": "Example", "company_identifier": "Example"}
        )
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].location, "Hyderabad, India")
        self.assertEqual(
            jobs[0].url,
            "https://jobs.smartrecruiters.com/Example/744-product-analyst",
        )


if __name__ == "__main__":
    unittest.main()
