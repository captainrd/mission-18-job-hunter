from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class HttpClient:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "Mission18-Job-Radar/1.0",
            }
        )
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST"),
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get_json(self, url: str, **kwargs: Any) -> dict[str, Any] | list[Any]:
        response = self.session.get(url, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def post_json(self, url: str, **kwargs: Any) -> dict[str, Any] | list[Any]:
        response = self.session.post(url, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response.json()

