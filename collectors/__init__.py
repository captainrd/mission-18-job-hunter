from collectors.greenhouse import GreenhouseCollector
from collectors.lever import LeverCollector
from collectors.oracle import OracleCollector
from collectors.smartrecruiters import SmartRecruitersCollector
from collectors.workday import WorkdayCollector

COLLECTORS = {
    "greenhouse": GreenhouseCollector,
    "lever": LeverCollector,
    "oracle": OracleCollector,
    "smartrecruiters": SmartRecruitersCollector,
    "workday": WorkdayCollector,
}

