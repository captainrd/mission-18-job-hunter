from collectors.ashby import AshbyCollector
from collectors.custom_html import CustomHtmlCollector
from collectors.greenhouse import GreenhouseCollector
from collectors.lever import LeverCollector
from collectors.oracle import OracleCollector
from collectors.smartrecruiters import SmartRecruitersCollector
from collectors.workday import WorkdayCollector

COLLECTORS = {
    "ashby": AshbyCollector,
    "custom_html": CustomHtmlCollector,
    "greenhouse": GreenhouseCollector,
    "lever": LeverCollector,
    "oracle": OracleCollector,
    "smartrecruiters": SmartRecruitersCollector,
    "workday": WorkdayCollector,
}

