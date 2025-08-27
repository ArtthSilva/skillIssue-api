from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from typing import Iterable, List
from .base import BaseScraper
from .models import Job

class IndeedScraper(BaseScraper):
    def search(self, query: str, location: str = "Brasil", limit: int = 50) -> Iterable[Job]:
        q = query.replace(" ", "+")
        base = f"https://br.indeed.com/jobs?q={q}&l={location}"
        results: List[Job] = []

        def parse_cards(html: str) -> List[Job]:
            out: List[Job] = []
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select("a.tapItem"):
                title = card.select_one("h2.jobTitle")
                company = card.select_one("span.companyName")
                location_el = card.select_one("div.companyLocation")
                desc = card.select_one("div.job-snippet")
                href = card.get("href")
                out.append(Job(
                    title=title.get_text(strip=True) if title else "N/A",
                    company=company.get_text(strip=True) if company else "N/A",
                    location=location_el.get_text(strip=True) if location_el else "N/A",
                    desc=desc.get_text(" ", strip=True) if desc else "",
                    source="indeed",
                    url=("https://br.indeed.com" + href) if href and href.startswith("/") else href
                ))
            return out

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
            )
            context.set_extra_http_headers({
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
                "DNT": "1",
            })

            def route_handler(route):
                rt = route.request.resource_type
                if rt in {"image", "font", "stylesheet"}:
                    return route.abort()
                return route.continue_()

            context.route("**/*", route_handler)
            page = context.new_page()

            start = 0
            while len(results) < limit:
                url = base if start == 0 else f"{base}&start={start}"
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass

                try:
                    page.locator("#onetrust-accept-btn-handler").click(timeout=2000)
                except Exception:
                    pass

                try:
                    page.wait_for_selector("a.tapItem", timeout=8000)
                except Exception:
                    page.wait_for_timeout(2000)

                html = page.content()
                try:
                    with open(f"data/debug_indeed_{start}.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    page.screenshot(path=f"data/debug_indeed_{start}.png", full_page=True)
                except Exception:
                    pass
                page_jobs = parse_cards(html)
                if not page_jobs and start > 0:
                    break
                for job in page_jobs:
                    results.append(job)
                    if len(results) >= limit:
                        break

                start += 10

            browser.close()
        return results
