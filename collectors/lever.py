from collectors.base import Collector
from core.models import RawJob


class LeverCollector(Collector):
    def collect(self, company: dict[str, object]) -> list[RawJob]:
        site = self.require(company, "site")
        data = self.client.get_json(
            f"https://api.lever.co/v0/postings/{site}", params={"mode": "json"}
        )
        assert isinstance(data, list)
        jobs = []
        for item in data:
            categories = item.get("categories") or {}
            location = categories.get("location") or item.get("workplaceType", "")
            lists = item.get("lists") or []
            description = " ".join(
                str(section.get("content", "")) for section in lists
            )
            jobs.append(
                RawJob(
                    external_id=str(item.get("id", "")),
                    title=str(item.get("text", "")),
                    location=str(location),
                    url=str(item.get("hostedUrl", "")),
                    description=f"{item.get('descriptionPlain', '')} {description}",
                )
            )
        return jobs

