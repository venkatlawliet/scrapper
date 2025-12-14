from .job_models import (
    JobPosting,
    JobScrapeRequest,
    JobScrapeResult,
    JobSite,
    JobType,
    LocationType,
)
try:
    from src.db_models import CompanySQL, JobSQL
except ImportError:
    CompanySQL = None
    JobSQL = None
__all__ = [
    "JobPosting",
    "JobScrapeRequest",
    "JobScrapeResult",
    "JobSite",
    "JobType",
    "LocationType",
]
if CompanySQL is not None:
    __all__.extend(["CompanySQL", "JobSQL"])