import hashlib
import html
import re
from datetime import datetime, timezone

from core.models import Job, RawJob


TAG_PATTERN = re.compile(r"<[^>]+>")
SPACE_PATTERN = re.compile(r"\s+")


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    without_tags = TAG_PATTERN.sub(" ", html.unescape(str(value)))
    return SPACE_PATTERN.sub(" ", without_tags).strip()


def normalize_date(value: str | None) -> str:
    if not value:
        return ""
    text = str(value).strip()
    normalized = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).date().isoformat()
    except ValueError:
        return text


def normalize_job(raw: RawJob, company: dict[str, object]) -> Job:
    title = clean_text(raw.title)
    location = clean_text(raw.location)
    url = str(raw.url).strip()
    external_id = str(raw.external_id).strip()
    if not external_id:
        source = "|".join((str(company["name"]), title, location, url))
        external_id = hashlib.sha256(source.encode("utf-8")).hexdigest()[:24]

    return Job(
        job_id=external_id,
        title=title,
        company=str(company["name"]),
        location=location,
        url=url,
        posted_date=normalize_date(raw.posted_date),
        description=clean_text(raw.description),
        company_domain=str(company.get("domain", "")),
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

