import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from core.models import Job


def write_daily_report(
    report_dir: str | Path,
    scanned: int,
    accepted: int,
    new_jobs: list[Job],
    failures: list[str],
) -> tuple[Path, Path]:
    directory = Path(report_dir)
    directory.mkdir(parents=True, exist_ok=True)
    timezone_name = os.getenv("MISSION18_TIMEZONE", "Asia/Kolkata")
    day = datetime.now(ZoneInfo(timezone_name)).date().isoformat()
    payload = {
        "date": day,
        "jobs_scanned": scanned,
        "jobs_accepted": accepted,
        "new_jobs": [job.to_dict() for job in new_jobs],
        "collector_failures": failures,
    }
    json_path = directory / f"{day}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# Mission18 Daily Report - {day}",
        "",
        f"- Jobs scanned: {scanned}",
        f"- Jobs accepted: {accepted}",
        f"- New jobs: {len(new_jobs)}",
        f"- Collector failures: {len(failures)}",
        "",
        "## Opportunities",
        "",
    ]
    if not new_jobs:
        lines.append("No new matching opportunities.")
    for job in sorted(new_jobs, key=lambda item: item.score, reverse=True):
        lines.extend(
            [
                f"### {job.company} - {job.title}",
                "",
                f"- Location: {job.location}",
                f"- Score: {job.score}",
                f"- Job ID: {job.job_id}",
                f"- Apply: {job.url}",
                "",
            ]
        )
    if failures:
        lines.extend(["## Collector Failures", ""])
        lines.extend(f"- {failure}" for failure in failures)
    markdown_path = directory / f"{day}.md"
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path
