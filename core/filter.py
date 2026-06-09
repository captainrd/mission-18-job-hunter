import re
from dataclasses import dataclass

from core.models import Job


EXPERIENCE_PATTERNS = (
    re.compile(r"\b(\d{1,2})\s*(?:-|to)\s*(\d{1,2})\s*(?:years?|yrs?)\b", re.I),
    re.compile(r"\b(\d{1,2})\+?\s*(?:years?|yrs?)\b", re.I),
)


@dataclass(frozen=True, slots=True)
class FilterResult:
    accepted: bool
    reason: str = ""
    experience: tuple[int, int] | None = None


def extract_experience(text: str) -> tuple[int, int] | None:
    range_match = EXPERIENCE_PATTERNS[0].search(text)
    if range_match:
        low, high = (int(range_match.group(1)), int(range_match.group(2)))
        return min(low, high), max(low, high)
    single_match = EXPERIENCE_PATTERNS[1].search(text)
    if single_match:
        years = int(single_match.group(1))
        return years, years
    return None


class JobFilter:
    def __init__(self, config: dict[str, object]) -> None:
        self.include = [str(item).casefold() for item in config["include_keywords"]]
        self.exclude = [str(item).casefold() for item in config["exclude_keywords"]]
        self.locations = [str(item).casefold() for item in config["accepted_locations"]]
        experience = config["experience"]
        assert isinstance(experience, dict)
        self.minimum_years = int(experience["minimum_years"])
        self.maximum_years = int(experience["maximum_years"])
        self.reject_zero = bool(experience.get("reject_zero_years", True))
        self.reject_above = int(experience.get("reject_above_years", 10))

    def evaluate(self, job: Job) -> FilterResult:
        title = job.title.casefold()
        if not any(keyword in title for keyword in self.include):
            return FilterResult(False, "role_not_targeted")
        if any(keyword in title for keyword in self.exclude):
            return FilterResult(False, "excluded_seniority")

        location = job.location.casefold()
        if not any(candidate in location for candidate in self.locations):
            return FilterResult(False, "location_not_targeted")

        experience = extract_experience(f"{job.title} {job.description}")
        if experience:
            low, high = experience
            if self.reject_zero and high == 0:
                return FilterResult(False, "zero_experience")
            if low >= self.reject_above:
                return FilterResult(False, "experience_too_high")
            if high < self.minimum_years or low > self.maximum_years:
                return FilterResult(False, "experience_outside_target", experience)

        return FilterResult(True, experience=experience)

