import re
from urllib.parse import urljoin
from typing import Any

from bs4 import BeautifulSoup

from collectors.base import Collector
from core.models import RawJob


class CustomHtmlCollector(Collector):
    def collect(self, company: dict[str, object]) -> list[RawJob]:
        base_url = self.require(company, "base_url")
        list_selector = self.require(company, "list_selector")
        title_selector = self.require(company, "title_selector")
        location_selector = self.require(company, "location_selector")
        url_selector = self.require(company, "url_selector")
        id_selector = company.get("id_selector")
        id_attribute = company.get("id_attribute", "href")
        posted_date_selector = company.get("posted_date_selector")
        description_selector = company.get("description_selector")
        pagination = company.get("pagination")

        jobs: list[RawJob] = []
        seen_ids: set[str] = set()

        def extract_jobs_from_page(html: str, page_url: str) -> list[RawJob]:
            soup = BeautifulSoup(html, "html.parser")
            elements = soup.select(list_selector)
            page_jobs = []
            for el in elements:
                title_el = el.select_one(title_selector)
                location_el = el.select_one(location_selector)
                url_el = el.select_one(url_selector)
                if not title_el or not url_el:
                    continue
                title = title_el.get_text(strip=True)
                location = location_el.get_text(strip=True) if location_el else ""
                url = url_el.get("href") or url_el.get_text(strip=True)
                url = urljoin(page_url, url)

                if id_selector:
                    id_el = el.select_one(id_selector)
                    if id_el:
                        external_id = id_el.get(id_attribute, "").strip()
                    else:
                        external_id = ""
                else:
                    external_id = url

                if not external_id or external_id in seen_ids:
                    continue
                seen_ids.add(external_id)

                posted_date = ""
                if posted_date_selector:
                    date_el = el.select_one(posted_date_selector)
                    if date_el:
                        posted_date = date_el.get_text(strip=True)

                description = ""
                if description_selector:
                    desc_el = el.select_one(description_selector)
                    if desc_el:
                        description = desc_el.get_text(strip=True)

                page_jobs.append(
                    RawJob(
                        external_id=external_id,
                        title=title,
                        location=location,
                        url=url,
                        posted_date=posted_date,
                        description=description,
                    )
                )
            return page_jobs

        if pagination:
            page_template = pagination.get("page_template")
            start = int(pagination.get("start", 1))
            max_pages = int(pagination.get("max_pages", 10))
            for page in range(start, start + max_pages):
                page_url = page_template.format(page=page)
                try:
                    response = self.client.session.get(page_url, timeout=self.client.timeout)
                    response.raise_for_status()
                    page_jobs = extract_jobs_from_page(response.text, page_url)
                    if not page_jobs:
                        break
                    jobs.extend(page_jobs)
                except Exception:
                    break
        else:
            try:
                response = self.client.session.get(base_url, timeout=self.client.timeout)
                response.raise_for_status()
                jobs.extend(extract_jobs_from_page(response.text, base_url))
            except Exception:
                pass

        return jobs
