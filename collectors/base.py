from abc import ABC, abstractmethod

from core.fetch import HttpClient
from core.models import RawJob


class Collector(ABC):
    def __init__(self, client: HttpClient | None = None) -> None:
        self.client = client or HttpClient()

    @abstractmethod
    def collect(self, company: dict[str, object]) -> list[RawJob]:
        raise NotImplementedError

    @staticmethod
    def require(company: dict[str, object], key: str) -> str:
        value = str(company.get(key, "")).strip()
        if not value:
            raise ValueError(f"{company.get('name', 'Company')}: missing '{key}'")
        return value

