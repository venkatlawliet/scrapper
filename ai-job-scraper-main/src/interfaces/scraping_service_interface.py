from abc import abstractmethod
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from typing import Any, Protocol
from pydantic import BaseModel
from src.schemas import Job
class SourceType(Enum):
    JOB_BOARDS = "job_boards"  
    COMPANY_PAGES = "company_pages"  
    UNIFIED = "unified" 
class ScrapingStatus(BaseModel):
    task_id: str
    status: str  
    progress_percentage: float
    jobs_found: int
    jobs_processed: int
    source_type: SourceType
    start_time: datetime
    end_time: datetime | None = None
    error_message: str | None = None
    success_rate: float = 0.0
class JobQuery(BaseModel):
    keywords: list[str]
    locations: list[str] = ["Remote"]
    source_types: list[SourceType] = [SourceType.UNIFIED]
    max_results: int = 100
    hours_old: int = 72
    enable_ai_enhancement: bool = True
    concurrent_requests: int = 10
class IScrapingService(Protocol):
    @abstractmethod
    async def scrape_unified(self, query: JobQuery) -> list[Job]:
        ...
    @abstractmethod
    async def scrape_job_boards_async(self, query: JobQuery) -> list[Job]:
        ...
    @abstractmethod
    async def scrape_company_pages_async(self, query: JobQuery) -> list[Job]:
        ...
    @abstractmethod
    async def enhance_job_data(self, jobs: list[Job]) -> list[Job]:
        ...
    @abstractmethod
    async def start_background_scraping(self, query: JobQuery) -> str:
        ...
    @abstractmethod
    async def get_scraping_status(self, task_id: str) -> ScrapingStatus:
        ...
    @abstractmethod
    async def monitor_scraping_progress(
        self, task_id: str
    ) -> AsyncGenerator[ScrapingStatus, None]:
        ...
    @abstractmethod
    async def get_success_rate_metrics(self) -> dict[str, Any]:
        ...
class ScrapingServiceError(Exception):
    def __init__(self, message: str, source_type: SourceType | None = None):
        super().__init__(message)
        self.source_type = source_type
class JobBoardScrapingError(ScrapingServiceError):
    def __init__(self, message: str):
        super().__init__(message, SourceType.JOB_BOARDS)
class CompanyPageScrapingError(ScrapingServiceError):
    def __init__(self, message: str):
        super().__init__(message, SourceType.COMPANY_PAGES)
class AIEnhancementError(ScrapingServiceError):
    def __init__(self, message: str):
        super().__init__(message, SourceType.UNIFIED)