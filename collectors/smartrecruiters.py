import re

from collectors.base import Collector
from core.models import RawJob


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


class SmartRecruitersCollector(Collector):
    def collect(self, company: dict[str, object]) -> list[RawJob]:
        identifier = self.require(company, "company_identifier")
        url = f"https://api.smartrecruiters.com/v1/companies/{identifier}/postings"
        offset = 0
        jobs = []
        while True:
            data = self.client.get_json(url, params={"limit": 100, "offset": offset})
            assert isinstance(data, dict)
            content = data.get("content", [])
            for item in content:
                location_data = item.get("location") or {}
                location = str(
                    location_data.get("fullLocation")
                    or ", ".join(
                        str(location_data.get(key, ""))
                        for key in ("city", "region", "country")
                        if location_data.get(key)
                    )
                )
                title = str(item.get("name", ""))
                external_id = str(item.get("id", ""))
                jobs.append(
                    RawJob(
                        external_id=external_id,
                        title=title,
                        location=location,
                        url=(
                            f"https://jobs.smartrecruiters.com/{identifier}/"
                            f"{external_id}-{slugify(title)}"
                        ),
                        posted_date=str(item.get("releasedDate", "")),
                    )
                )
            offset += len(content)
            total = int(data.get("totalFound", len(content)))
            if not content or offset >= total:
                break
        return jobs
