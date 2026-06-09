# Mission18 Job Radar

Mission18 is a zero-cost Python job discovery pipeline. It collects jobs from
supported applicant tracking systems, normalizes and filters them, assigns a
score, stores deduplication state in SQLite, and sends Telegram alerts.

## Features

- Workday, Greenhouse, Lever, SmartRecruiters, and Oracle HCM connectors
- YAML-driven companies, target roles, locations, experience, and scoring
- SQLite deduplication across scheduled runs
- Individual opportunity alerts and a run digest through Telegram
- Markdown and JSON daily reports
- GitHub Actions schedule at 06:00, 12:00, and 18:00 India Standard Time
- Collector isolation: one unavailable company does not stop other scans

## Local Setup

Python 3.12 is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py --dry-run --verbose
```

If `python -m venv .venv` fails on Windows, the application can also run with
packages installed into your existing Python installation:

```powershell
python -m pip install -r requirements.txt
python main.py --dry-run --verbose
```

On Windows, production data is stored outside the source folder by default:

```text
%LOCALAPPDATA%\Mission18\database\jobs.db
%LOCALAPPDATA%\Mission18\reports\daily
```

Override these with `MISSION18_DATA_DIR`, `MISSION18_DATABASE_PATH`, or
`MISSION18_REPORT_DIR`.

## Configure Companies

All Phase 1 companies are listed in `config/companies.yaml` but are disabled
until their ATS identifiers are supplied. This avoids silently scraping an
incorrect tenant when companies change careers platforms.

Common settings:

| Connector | Required settings |
| --- | --- |
| Greenhouse | `board_token` |
| Lever | `site` |
| SmartRecruiters | `company_identifier` |
| Workday | `base_url`, `tenant`, `site` |
| Oracle | public recruiting requisitions `api_url` |

Find these identifiers in the company's public careers URL or browser network
requests. Set `enabled: true` only after testing the entry:

```powershell
python main.py --dry-run --verbose
```

Example Greenhouse entry:

```yaml
- name: Example Company
  domain: product
  connector: greenhouse
  enabled: true
  board_token: examplecompany
```

Example Workday entry:

```yaml
- name: Example Bank
  domain: banking
  connector: workday
  enabled: true
  base_url: https://example.wd5.myworkdayjobs.com
  tenant: example
  site: External
```

## Telegram Setup

1. Create a bot with Telegram's `@BotFather`.
2. Send the bot a message and obtain the target chat ID.
3. Set the following environment variables locally:

```powershell
$env:TELEGRAM_BOT_TOKEN = "..."
$env:TELEGRAM_CHAT_ID = "..."
python main.py
```

For GitHub Actions, add repository secrets named `TELEGRAM_BOT_TOKEN` and
`TELEGRAM_CHAT_ID`.

## Commands

```powershell
# Fetch and print matches without persistence, report files, or Telegram
python main.py --dry-run

# Persist jobs but skip Telegram
python main.py --no-notify

# Normal production run
python main.py

# Production run with the daily digest
python main.py --digest

# Run tests
python -m unittest discover -s tests -v
```

## Persistence in GitHub Actions

The workflow restores the newest SQLite database from GitHub Actions cache and
saves an updated cache after each run. Daily reports are uploaded as workflow
artifacts for 30 days. GitHub cache retention policies apply; running the
workflow regularly keeps state fresh.

## Notes

- GitHub cron uses UTC, so the workflow uses `30 0,6,12 * * *` for 06:00,
  12:00, and 18:00 IST.
- ATS APIs can change without notice. A failed company is recorded in the daily
  report while remaining collectors continue.
- Job descriptions do not always state experience. Missing experience is
  accepted by the filter but receives no experience points.
