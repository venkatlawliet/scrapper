import asyncio
import logging
from typing import Any
import pandas as pd
from jobspy import scrape_jobs
from src.models.job_models import (
    JobPosting,
    JobScrapeRequest,
    JobScrapeResult,
    JobSite,
)
logger = logging.getLogger(__name__)
class JobSpyScraper:
    def __init__(self) -> None:
        self.default_settings = {
            "results_wanted": 100,
            "country_indeed": "USA",
            "linkedin_fetch_description": True,
            "linkedin_company_fetch_description": True,
            "description_format": "markdown",
        }
    async def scrape_jobs_async(self, request: JobScrapeRequest) -> JobScrapeResult:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.scrape_jobs_sync, request)
    def scrape_jobs_sync(self, request: JobScrapeRequest) -> JobScrapeResult:
        try:
            scrape_params = self._build_scrape_params(request)
            logger.info("Starting JobSpy scraping with params: %s", scrape_params)
            jobs_df = scrape_jobs(**scrape_params)
            if jobs_df is None or jobs_df.empty:
                logger.warning("JobSpy returned empty or None DataFrame")
                return self._empty_result(request)
            logger.info("JobSpy found %d jobs", len(jobs_df))
            jobs = self._dataframe_to_models(jobs_df, request.site_name)
            return JobScrapeResult(
                jobs=jobs,
                total_found=len(jobs),
                request_params=request,
                metadata={"scraping_method": "jobspy", "success": True},
            )
        except Exception:
            logger.exception("JobSpy scraping failed")
            return self._empty_result(request, error="Scraping operation failed")
    def _build_scrape_params(self, request: JobScrapeRequest) -> dict[str, Any]:
        params = self.default_settings.copy()
        if isinstance(request.site_name, list):
            params["site_name"] = [site.value for site in request.site_name]
        else:
            params["site_name"] = [request.site_name.value]
        params.update(
            {
                "search_term": request.search_term,
                "google_search_term": request.google_search_term,
                "location": request.location,
                "distance": request.distance,
                "is_remote": request.is_remote,
                "results_wanted": request.results_wanted,
                "country_indeed": request.country_indeed,
                "offset": request.offset,
                "hours_old": request.hours_old,
                "enforce_annual_salary": request.enforce_annual_salary,
                "linkedin_fetch_description": request.linkedin_fetch_description,
                "description_format": request.description_format,
            }
        )
        if request.job_type:
            params["job_type"] = request.job_type.value
        if request.easy_apply is not None:
            params["easy_apply"] = request.easy_apply
        return {k: v for k, v in params.items() if v is not None}
    def _dataframe_to_models(
        self, jobs_df: pd.DataFrame, _requested_sites: list[JobSite] | JobSite
    ) -> list[JobPosting]:
        jobs = []
        for _, row in jobs_df.iterrows():
            try:
                job_data = {}
                for col, value in row.items():
                    if pd.isna(value) or (isinstance(value, str) and not value.strip()):
                        job_data[col] = None
                    elif isinstance(value, (pd.Timestamp, pd.DatetimeIndex)):
                        job_data[col] = value.date() if hasattr(value, "date") else None
                    else:
                        job_data[col] = value
                if "id" not in job_data or not job_data["id"]:
                    job_data["id"] = f"job_{len(jobs)}_{hash(str(job_data))}"
                job_data["min_amount"] = self._safe_float(job_data.get("min_amount"))
                job_data["max_amount"] = self._safe_float(job_data.get("max_amount"))
                job_data["company_rating"] = self._safe_float(
                    job_data.get("company_rating")
                )
                job_posting = JobPosting.model_validate(job_data)
                jobs.append(job_posting)
            except Exception:
                logger.warning("Failed to convert job row to model")
                continue
        logger.info("Successfully converted %d jobs to Pydantic models", len(jobs))
        return jobs
    def _safe_float(self, value: Any) -> float | None:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    def _empty_result(
        self, request: JobScrapeRequest, error: str | None = None
    ) -> JobScrapeResult:
        metadata = {"scraping_method": "jobspy", "success": False}
        if error:
            metadata["error"] = error
        return JobScrapeResult(
            jobs=[],
            total_found=0,
            request_params=request,
            metadata=metadata,
        )
job_scraper = JobSpyScraper()
async def scrape_jobs_by_query(
    query: str,
    location: str | None = None,
    sites: list[str] | None = None,
    count: int = 100,
) -> list[dict[str, Any]]:
    try:
        site_enums = []
        if sites:
            for site in sites:
                site_enum = JobSite.normalize(site)
                if site_enum:
                    site_enums.append(site_enum)
        if not site_enums:
            site_enums = [JobSite.LINKEDIN]  
        request = JobScrapeRequest(
            site_name=site_enums,
            search_term=query,
            location=location,
            results_wanted=count,
        )
        result = await job_scraper.scrape_jobs_async(request)
        return [job.model_dump() for job in result.jobs]
    except Exception:
        logger.exception("Legacy scrape_jobs_by_query failed")
        return []