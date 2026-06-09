from collectors.base import Collector
from core.models import RawJob


class OracleCollector(Collector):
    def collect(self, company: dict[str, object]) -> list[RawJob]:
        api_url = self.require(company, "api_url")
        site_number = self.require(company, "site_number")
        career_url = self.require(company, "career_url").rstrip("/")
        search_keywords = company.get("search_keywords") or [""]
        search_location = str(company.get("search_location", "")).strip()
        limit = int(company.get("page_size", 100))
        facets = "TITLES;LOCATIONS;CATEGORIES;POSTING_DATES"
        jobs_by_id: dict[str, RawJob] = {}

        for keyword in search_keywords:
            offset = 0
            while True:
                finder_parts = [
                    f"siteNumber={site_number}",
                    f"facetsList={facets}",
                    f"limit={limit}",
                    f"offset={offset}",
                ]
                if keyword:
                    finder_parts.append(f"keyword={keyword}")
                if search_location:
                    finder_parts.append(f"location={search_location}")
                finder = "findReqs;" + ",".join(finder_parts)
                data = self.client.get_json(
                    api_url,
                    params={
                        "onlyData": "true",
                        "expand": (
                            "requisitionList.workLocation,"
                            "requisitionList.otherWorkLocations,"
                            "requisitionList.secondaryLocations,"
                            "requisitionList.requisitionFlexFields"
                        ),
                        "finder": finder,
                    },
                )
                assert isinstance(data, dict)
                search_results = data.get("items", [])
                if not search_results:
                    break
                search_result = search_results[0]
                requisitions = search_result.get("requisitionList", [])
                for item in requisitions:
                    external_id = str(
                        item.get("Id")
                        or item.get("RequisitionId")
                        or item.get("JobId", "")
                    )
                    description = " ".join(
                        str(item.get(field, ""))
                        for field in (
                            "ShortDescriptionStr",
                            "ExternalResponsibilitiesStr",
                            "ExternalQualificationsStr",
                        )
                    )
                    jobs_by_id[external_id] = RawJob(
                        external_id=external_id,
                        title=str(
                            item.get("Title")
                            or item.get("RequisitionTitle")
                            or item.get("Name", "")
                        ),
                        location=str(
                            item.get("PrimaryLocation")
                            or item.get("Location")
                            or item.get("JobLocation", "")
                        ),
                        url=f"{career_url}/{external_id}",
                        posted_date=str(
                            item.get("PostedDate")
                            or item.get("ExternalPostedStartDate", "")
                        ),
                        description=description,
                    )
                offset += len(requisitions)
                total = int(search_result.get("TotalJobsCount", len(requisitions)))
                if not requisitions or offset >= total:
                    break

        return list(jobs_by_id.values())
