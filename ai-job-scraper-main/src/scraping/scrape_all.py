import asyncio
import logging
from src.services.job_service import job_service
logger = logging.getLogger(__name__)
async def scrape_all() -> dict[str, int]:
    logger.info("Starting modern scrape_all using JobSpy integration")
    total_stats = {"inserted": 0, "updated": 0, "skipped": 0}
    try:
        search_terms = [
            "software engineer",
            "data scientist",
            "product manager",
            "marketing manager",
            "sales representative",
        ]
        sites = ["linkedin", "indeed", "glassdoor"]
        for search_term in search_terms:
            try:
                logger.info("Scraping jobs for: %s", search_term)
                result = await job_service.search_and_save_jobs(
                    search_term=search_term,
                    location="United States",
                    sites=sites,
                    results_wanted=50,  
                    save_to_db=True,
                )
                jobs_found = len(result.jobs)
                total_stats["inserted"] += jobs_found
                logger.info("Found %d jobs for '%s'", jobs_found, search_term)
            except Exception as e:
                logger.warning("Failed to scrape jobs for '%s': %s", search_term, e)
                continue
    except Exception:
        logger.exception("Critical error in scrape_all")
        return {"inserted": 0, "updated": 0, "skipped": 0}
    else:
        logger.info("Scrape_all completed successfully. Stats: %s", total_stats)
        return total_stats
def scrape_all_sync() -> dict[str, int]:
    try:
        return asyncio.run(scrape_all())
    except Exception:
        logger.exception("Failed to run scrape_all_sync")
        return {"inserted": 0, "updated": 0, "skipped": 0}