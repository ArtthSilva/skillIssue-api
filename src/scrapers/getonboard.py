import requests
from typing import Iterable, List
from .base import BaseScraper
from .models import Job

class GetOnBoardScraper(BaseScraper):
    def search(self, query: str, location: str = "Brasil", limit: int = 50) -> Iterable[Job]:
        url = f"https://www.getonbrd.com/api/v0/search/jobs?query={requests.utils.quote(query)}"
        try:
            r = requests.get(url, timeout=30, headers={"Accept": "application/json"})
            r.raise_for_status()
            data = r.json()
        except Exception:
            data = {"data": []}
        results: List[Job] = []
        for item in data.get("data", [])[:limit]:
            attrs = item.get("attributes", {})
            results.append(Job(
                title=attrs.get("title") or "N/A",
                company=(attrs.get("company", {}) or {}).get("name") or "N/A",
                location=attrs.get("remote_modality") or attrs.get("remote_zone") or "Remoto/LatAm",
                desc=attrs.get("description") or "",
                source="getonboard",
                url=attrs.get("external_url") or attrs.get("permalink")
            ))
        return results
