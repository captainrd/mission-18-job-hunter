from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class RawJob:
    title: str
    location: str
    url: str
    external_id: str = ""
    posted_date: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Job:
    job_id: str
    title: str
    company: str
    location: str
    url: str
    posted_date: str
    description: str = ""
    company_domain: str = ""
    score: int = 0
    status: str = "new"
    score_breakdown: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

