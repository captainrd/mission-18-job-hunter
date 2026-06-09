import argparse
import logging
import os
from pathlib import Path

import yaml

from collectors import COLLECTORS
from core.database import JobDatabase
from core.fetch import HttpClient
from core.filter import JobFilter
from core.normalize import normalize_job
from core.notify import TelegramNotifier
from core.report import write_daily_report
from core.score import JobScorer


ROOT = Path(__file__).resolve().parent
LOGGER = logging.getLogger("mission18")


def load_yaml(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping in {path}")
    return data


def default_data_directory() -> Path:
    local_app_data = os.getenv("LOCALAPPDATA")
    if os.name == "nt" and local_app_data:
        return Path(local_app_data) / "Mission18"
    return ROOT


def run(
    dry_run: bool = False, notify: bool = True, send_digest: bool = False
) -> int:
    companies_config = load_yaml(ROOT / "config" / "companies.yaml")
    roles = load_yaml(ROOT / "config" / "roles.yaml")
    scoring = load_yaml(ROOT / "config" / "scoring.yaml")
    companies = [
        company
        for company in companies_config.get("companies", [])
        if company.get("enabled", False)
    ]
    if not companies:
        LOGGER.warning(
            "No companies are enabled. Configure ATS identifiers in "
            "config/companies.yaml before running the radar."
        )
        return 0

    job_filter = JobFilter(roles)
    scorer = JobScorer(scoring, roles)
    client = HttpClient()
    notifier = TelegramNotifier()
    scanned = 0
    accepted = 0
    new_jobs = []
    failures = []
    successful_collectors = 0
    data_directory = Path(
        os.getenv("MISSION18_DATA_DIR", str(default_data_directory()))
    ).expanduser()

    database_path: str | Path
    if dry_run:
        database_path = ":memory:"
    else:
        database_path = Path(
            os.getenv(
                "MISSION18_DATABASE_PATH",
                str(data_directory / "database" / "jobs.db"),
            )
        ).expanduser()
    with JobDatabase(database_path, ROOT / "database" / "schema.sql") as database:
        for company in companies:
            name = str(company.get("name", "Unknown"))
            connector_name = str(company.get("connector", "")).casefold()
            collector_class = COLLECTORS.get(connector_name)
            if collector_class is None:
                failures.append(f"{name}: unknown connector '{connector_name}'")
                continue
            try:
                raw_jobs = collector_class(client).collect(company)
                successful_collectors += 1
                LOGGER.info("%s: collected %d jobs", name, len(raw_jobs))
                scanned += len(raw_jobs)
                for raw_job in raw_jobs:
                    job = normalize_job(raw_job, company)
                    result = job_filter.evaluate(job)
                    if not result.accepted:
                        continue
                    accepted += 1
                    scorer.score(job)
                    if dry_run:
                        if not database.is_seen(job):
                            new_jobs.append(job)
                    elif database.save(job):
                        new_jobs.append(job)
            except Exception as exc:
                LOGGER.exception("%s collector failed", name)
                failures.append(f"{name}: {exc}")

    new_jobs.sort(key=lambda item: item.score, reverse=True)
    if dry_run:
        for job in new_jobs:
            LOGGER.info(
                "MATCH score=%d company=%s title=%s location=%s url=%s",
                job.score,
                job.company,
                job.title,
                job.location,
                job.url,
            )
    else:
        report_directory = Path(
            os.getenv(
                "MISSION18_REPORT_DIR",
                str(data_directory / "reports" / "daily"),
            )
        ).expanduser()
        write_daily_report(
            report_directory, scanned, accepted, new_jobs, failures
        )

    if notify and not dry_run:
        for job in new_jobs:
            try:
                notifier.send_job(job)
            except Exception:
                LOGGER.exception("Failed to notify for %s/%s", job.company, job.job_id)
        if send_digest:
            try:
                notifier.send_digest(
                    scanned, new_jobs, int(scoring.get("high_score_threshold", 75))
                )
            except Exception:
                LOGGER.exception("Failed to send digest")

    LOGGER.info(
        "Complete: scanned=%d accepted=%d new=%d failures=%d",
        scanned,
        accepted,
        len(new_jobs),
        len(failures),
    )
    return 1 if companies and successful_collectors == 0 else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mission18 Job Radar")
    parser.add_argument(
        "--dry-run", action="store_true", help="Do not persist or send alerts"
    )
    parser.add_argument(
        "--no-notify", action="store_true", help="Persist jobs without Telegram alerts"
    )
    parser.add_argument(
        "--digest", action="store_true", help="Send the daily Telegram digest"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable debug-level logging"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    raise SystemExit(
        run(
            dry_run=args.dry_run,
            notify=not args.no_notify,
            send_digest=args.digest,
        )
    )
