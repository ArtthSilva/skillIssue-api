import requests
from typing import Iterable, List, Set
from .base import BaseScraper
from .models import Job


class RemotiveScraper(BaseScraper):
    def search(self, query: str, location: str = "Brasil", limit: int = 50) -> Iterable[Job]:
        synonyms = [
            query,
            query.replace("front end", "frontend"),
            query.replace("front-end", "frontend"),
            "frontend",
            "react",
            "javascript",
        ]
        seen: Set[str] = set()
        jobs: List[Job] = []
        for q in synonyms:
            if len(jobs) >= limit:
                break
            url = f"https://remotive.com/api/remote-jobs?search={requests.utils.quote(q)}"
            try:
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                data = r.json().get("jobs", [])
            except Exception:
                data = []
            for j in data:
                if len(jobs) >= limit:
                    break
                uid = j.get("url") or f"{j.get('title')}-{j.get('company_name')}"
                if not uid or uid in seen:
                    continue
                seen.add(uid)
                jobs.append(Job(
                    title=j.get("title", "N/A"),
                    company=j.get("company_name", "N/A"),
                    location=j.get("candidate_required_location", "Remoto"),
                    desc=j.get("description", ""),
                    source="remotive",
                    url=j.get("url")
                ))
        return jobs
