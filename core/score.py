from core.filter import extract_experience
from core.models import Job


class JobScorer:
    def __init__(self, scoring: dict[str, object], roles: dict[str, object]) -> None:
        self.maximum = int(scoring["maximum_score"])
        self.weights = {key: int(value) for key, value in scoring["weights"].items()}
        self.domain_keywords = {
            key: [str(item).casefold() for item in values]
            for key, values in scoring["domain_keywords"].items()
        }
        self.bonus_keywords = [
            str(item).casefold() for item in scoring.get("bonus_keywords", [])
        ]
        self.role_keywords = [
            str(item).casefold() for item in roles["include_keywords"]
        ]
        self.locations = [
            str(item).casefold() for item in roles["accepted_locations"]
        ]
        experience = roles["experience"]
        self.minimum_years = int(experience["minimum_years"])
        self.maximum_years = int(experience["maximum_years"])

    def score(self, job: Job) -> Job:
        searchable = f"{job.title} {job.description}".casefold()
        breakdown = {
            "role_match": self.weights["role_match"]
            if any(item in job.title.casefold() for item in self.role_keywords)
            else 0,
            "domain_match": self._domain_score(job, searchable),
            "experience_match": self._experience_score(searchable),
            "location_match": self.weights["location_match"]
            if any(item in job.location.casefold() for item in self.locations)
            else 0,
            "keyword_bonus": self.weights["keyword_bonus"]
            if any(item in searchable for item in self.bonus_keywords)
            else 0,
        }
        job.score_breakdown = breakdown
        job.score = min(sum(breakdown.values()), self.maximum)
        return job

    def _domain_score(self, job: Job, searchable: str) -> int:
        domain = job.company_domain.casefold()
        keywords = self.domain_keywords.get(domain, [])
        if domain in self.domain_keywords or any(item in searchable for item in keywords):
            return self.weights["domain_match"]
        return 0

    def _experience_score(self, searchable: str) -> int:
        experience = extract_experience(searchable)
        if experience is None:
            return 0
        low, high = experience
        if high >= self.minimum_years and low <= self.maximum_years:
            return self.weights["experience_match"]
        return 0

