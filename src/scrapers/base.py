from abc import ABC, abstractmethod
from typing import Iterable
from .models import Job

class BaseScraper(ABC):
    @abstractmethod
    def search(self, query: str, location: str = "Brasil", limit: int = 50) -> Iterable[Job]:
        raise NotImplementedError
