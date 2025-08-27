from .base import BaseScraper
from .models import Job
from typing import Iterable

class LinkedInScraper(BaseScraper):
    def search(self, query: str, location: str = "Brasil", limit: int = 50) -> Iterable[Job]:
        return []
