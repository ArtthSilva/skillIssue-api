from src.scrapers.indeed import IndeedScraper
from src.scrapers.linkedin_stub import LinkedInScraper
from src.scrapers.glassdoor_stub import GlassdoorScraper
from src.scrapers.remotive import RemotiveScraper
from src.scrapers.getonboard import GetOnBoardScraper
from src.skills.analyzer import aggregate_descriptions, top_n
import pandas as pd
from typing import List

SOURCES = {
    "indeed": IndeedScraper(),
    "linkedin": LinkedInScraper(),
    "glassdoor": GlassdoorScraper(),
    "remotive": RemotiveScraper(),
    "getonboard": GetOnBoardScraper(),
}

def collect_jobs(query: str, location: str = "Brasil", limit: int = 50, sources: List[str] = None):
    if sources is None:
        sources = list(SOURCES.keys())
    jobs = []
    for name in sources:
        scraper = SOURCES.get(name)
        if not scraper:
            continue
        try:
            jobs.extend(list(scraper.search(query=query, location=location, limit=limit)))
        except Exception as e:
            print(f"[WARN] Falha na fonte {name}: {e}")
    return jobs

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--location", default="Brasil")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--sources", nargs="*", default=["getonboard","remotive"])  # usar fontes sem cf
    args = parser.parse_args()

    jobs = collect_jobs(args.query, args.location, args.limit, args.sources)
    # Dedup: prioriza URL; fallback para (title, company, location)
    seen_keys = set()
    unique_jobs = []
    for j in jobs:
        key = j.url or (j.title, j.company, j.location)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique_jobs.append(j)
    jobs = unique_jobs
    print(f"Coletadas {len(jobs)} vagas (dedup) de {args.sources}.")

    descs = [j.desc for j in jobs if j.desc]
    agg = aggregate_descriptions(descs)
    top = top_n(agg, 15)

    # Export simples
    df = pd.DataFrame([j.__dict__ for j in jobs])
    df.to_csv("data/jobs.csv", index=False)

    for k, items in top.items():
        print("\nTop", k)
        for w, c in items:
            print(f"{w}: {c}")
