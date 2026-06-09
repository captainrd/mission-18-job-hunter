import html
import logging
import os

import requests

from core.models import Job


LOGGER = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, token: str | None = None, chat_id: str | None = None) -> None:
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")

    @property
    def configured(self) -> bool:
        return bool(self.token and self.chat_id)

    def send_job(self, job: Job) -> bool:
        message = (
            "<b>New Mission18 Opportunity</b>\n\n"
            f"<b>Company:</b> {html.escape(job.company)}\n"
            f"<b>Role:</b> {html.escape(job.title)}\n"
            f"<b>Location:</b> {html.escape(job.location)}\n"
            f"<b>Score:</b> {job.score}\n"
            f"<b>Job ID:</b> {html.escape(job.job_id)}\n\n"
            f'<a href="{html.escape(job.url, quote=True)}">Apply</a>'
        )
        return self._send(message)

    def send_digest(
        self, scanned: int, new_jobs: list[Job], high_score_threshold: int
    ) -> bool:
        high_score = [job for job in new_jobs if job.score >= high_score_threshold]
        top_companies = list(dict.fromkeys(job.company for job in new_jobs))[:5]
        companies = ", ".join(top_companies) if top_companies else "None"
        message = (
            "<b>Mission18 Daily Digest</b>\n\n"
            f"<b>Jobs scanned:</b> {scanned}\n"
            f"<b>New jobs:</b> {len(new_jobs)}\n"
            f"<b>High score jobs:</b> {len(high_score)}\n"
            f"<b>Top companies:</b> {html.escape(companies)}"
        )
        return self._send(message)

    def _send(self, message: str) -> bool:
        if not self.configured:
            LOGGER.info("Telegram is not configured; notification skipped")
            return False
        response = requests.post(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            json={
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        response.raise_for_status()
        return True

