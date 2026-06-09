from collectors.base import Collector
from core.models import RawJob


class GreenhouseCollector(Collector):
    def collect(self, company: dict[str, object]) -> list[RawJob]:
        token = self.require(company, "board_token")
        data = self.client.get_json(
            f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs",
            params={"content": "true"},
        )
        assert isinstance(data, dict)
        jobs = []
        for item in data.get("jobs", []):
            location = item.get("location") or {}
            jobs.append(
                RawJob(
                    external_id=str(item.get("id", "")),
                    title=str(item.get("title", "")),
                    location=str(location.get("name", "")),
                    url=str(item.get("absolute_url", "")),
                    posted_date=str(item.get("updated_at", "")),
                    description=str(item.get("content", "")),
                )
            )
        return jobs

