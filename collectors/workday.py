from urllib.parse import urljoin

from collectors.base import Collector
from core.models import RawJob


class WorkdayCollector(Collector):
    def collect(self, company: dict[str, object]) -> list[RawJob]:
        base_url = self.require(company, "base_url").rstrip("/")
        tenant = self.require(company, "tenant")
        site = self.require(company, "site")
        api_url = f"{base_url}/wday/cxs/{tenant}/{site}/jobs"
        offset = 0
        jobs = []
        while True:
            data = self.client.post_json(
                api_url,
                json={
                    "appliedFacets": {},
                    "limit": 20,
                    "offset": offset,
                    "searchText": "",
                },
            )
            assert isinstance(data, dict)
            postings = data.get("jobPostings", [])
            for item in postings:
                external_path = str(item.get("externalPath", ""))
                jobs.append(
                    RawJob(
                        external_id=str(
                            item.get("bulletFields", [""])[0] if item.get("bulletFields") else ""
                        ),
                        title=str(item.get("title", "")),
                        location=str(item.get("locationsText", "")),
                        url=urljoin(f"{base_url}/", f"{site}{external_path}"),
                        posted_date=str(item.get("postedOn", "")),
                    )
                )
            offset += len(postings)
            total = int(data.get("total", len(postings)))
            if not postings or offset >= total:
                break
        return jobs

