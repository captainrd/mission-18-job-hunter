from collectors.base import Collector
from core.models import RawJob


class AshbyCollector(Collector):
    def collect(self, company: dict[str, object]) -> list[RawJob]:
        job_board_name = self.require(company, "job_board_name")
        url = f"https://api.ashbyhq.com/posting-api/job-board/{job_board_name}"
        data = self.client.get_json(url)
        assert isinstance(data, dict)
        jobs = []
        for item in data.get("jobs", []):
            external_id = str(item.get("id", ""))
            title = str(item.get("title", ""))
            location = str(item.get("location", ""))
            job_url = str(item.get("jobUrl", ""))
            apply_url = str(item.get("applyUrl", ""))
            posted_date = str(item.get("publishedAt", ""))
            description = str(item.get("descriptionPlain", ""))
            url_to_use = apply_url or job_url
            jobs.append(
                RawJob(
                    external_id=external_id,
                    title=title,
                    location=location,
                    url=url_to_use,
                    posted_date=posted_date,
                    description=description,
                )
            )
        return jobs
