from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from typing import Optional, List, Dict, Any
from src.skills.analyzer import aggregate_descriptions, top_n
from src.scrapers.indeed import IndeedScraper
from src.scrapers.linkedin_stub import LinkedInScraper
from src.scrapers.glassdoor_stub import GlassdoorScraper
from src.scrapers.remotive import RemotiveScraper
from src.scrapers.getonboard import GetOnBoardScraper
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

app = FastAPI(title="Radar de Vagas API", version="0.1.0")

# Instâncias dos scrapers
SCRAPERS = {
    "indeed": IndeedScraper(),
    "linkedin": LinkedInScraper(),
    "glassdoor": GlassdoorScraper(),
    "remotive": RemotiveScraper(),
    "getonboard": GetOnBoardScraper(),
}

def load_jobs(path: str = "data/jobs.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.DataFrame(columns=["title","company","location","desc","source","url"]) 
    return df.fillna("")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/skills")
def get_skills(
    q: Optional[str] = Query(None, description="Texto para filtrar por título/descrição"),
    location: Optional[str] = Query(None, description="Filtro por localização"),
    source: Optional[str] = Query(None, description="Fonte: linkedin, remotive, etc."),
    top: int = Query(10, ge=1, le=50, description="Quantidade de itens por categoria"),
):
    df = load_jobs()
    if df.empty:
        return JSONResponse({"dev": [], "cloud": [], "soft": []})

    # Filtros simples
    mask = pd.Series([True] * len(df))
    if q:
        ql = q.lower()
        mask &= df["title"].str.lower().str.contains(ql) | df["desc"].str.lower().str.contains(ql)
    if location:
        ll = location.lower()
        mask &= df["location"].str.lower().str.contains(ll)
    if source:
        sl = source.lower()
        mask &= df["source"].str.lower() == sl

    descs: List[str] = df.loc[mask, "desc"].dropna().astype(str).tolist()
    agg = aggregate_descriptions(descs)
    tops = top_n(agg, top)
    return tops

def run_scraper_sync(scraper_name: str, query: str, location: str, limit: int):
    """Executa scraper de forma síncrona"""
    scraper = SCRAPERS.get(scraper_name)
    if not scraper:
        raise HTTPException(status_code=400, detail=f"Scraper '{scraper_name}' não encontrado")
    
    try:
        jobs = list(scraper.search(query=query, location=location, limit=limit))
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no scraping {scraper_name}: {str(e)}")

@app.post("/scrape/{source}")
async def scrape_source(
    source: str,
    query: str = Query(..., description="Termo de busca"),
    location: str = Query("Brasil", description="Localização"),
    limit: int = Query(20, ge=1, le=100, description="Limite de vagas"),
    save_to_csv: bool = Query(True, description="Salvar resultados em CSV")
):
    """
    Executa scraping de uma fonte específica
    
    Fontes disponíveis: indeed, linkedin, glassdoor, remotive, getonboard
    """
    if source not in SCRAPERS:
        available = list(SCRAPERS.keys())
        raise HTTPException(status_code=400, detail=f"Fonte '{source}' não disponível. Fontes: {available}")
    
    try:
        # Executa scraping em thread separada para não bloquear
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_scraper_sync, source, query, location, limit)
            jobs = future.result(timeout=300)  # 5 minutos timeout
        
        if not jobs:
            return {
                "source": source,
                "query": query,
                "location": location,
                "jobs_found": 0,
                "jobs": [],
                "skills": {"dev": [], "cloud": [], "soft": []}
            }
        
        # Analizar skills das vagas encontradas
        descriptions = [job.desc for job in jobs if job.desc]
        skills_agg = aggregate_descriptions(descriptions) if descriptions else {"dev": [], "cloud": [], "soft": []}
        skills_top = top_n(skills_agg, 10)
        
        # Converter jobs para dict
        jobs_data = [
            {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.desc,
                "source": job.source,
                "url": job.url
            }
            for job in jobs
        ]
        
        # Salvar em CSV se solicitado
        if save_to_csv:
            df_existing = load_jobs()
            df_new = pd.DataFrame(jobs_data)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            
            # Remover duplicatas por URL
            df_combined = df_combined.drop_duplicates(subset=['url'], keep='last')
            df_combined.to_csv("data/jobs.csv", index=False)
        
        return {
            "source": source,
            "query": query,
            "location": location,
            "jobs_found": len(jobs),
            "jobs": jobs_data,
            "skills": skills_top,
            "saved_to_csv": save_to_csv
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no scraping: {str(e)}")

@app.post("/scrape/multiple")
async def scrape_multiple_sources(
    query: str = Query(..., description="Termo de busca"),
    location: str = Query("Brasil", description="Localização"),
    limit: int = Query(20, ge=1, le=100, description="Limite de vagas por fonte"),
    sources: List[str] = Query(["remotive", "getonboard"], description="Lista de fontes"),
    save_to_csv: bool = Query(True, description="Salvar resultados em CSV")
):
    """
    Executa scraping de múltiplas fontes em paralelo
    
    Fontes disponíveis: indeed, linkedin, glassdoor, remotive, getonboard
    """
    available_sources = list(SCRAPERS.keys())
    invalid_sources = [s for s in sources if s not in available_sources]
    if invalid_sources:
        raise HTTPException(
            status_code=400, 
            detail=f"Fontes inválidas: {invalid_sources}. Disponíveis: {available_sources}"
        )
    
    all_jobs = []
    results_by_source = {}
    
    try:
        # Executa scrapers em paralelo
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            future_to_source = {
                executor.submit(run_scraper_sync, source, query, location, limit): source 
                for source in sources
            }
            
            for future in future_to_source:
                source = future_to_source[future]
                try:
                    jobs = future.result(timeout=300)
                    all_jobs.extend(jobs)
                    results_by_source[source] = {
                        "jobs_found": len(jobs),
                        "success": True,
                        "error": None
                    }
                except Exception as e:
                    results_by_source[source] = {
                        "jobs_found": 0,
                        "success": False,
                        "error": str(e)
                    }
        
        # Remover duplicatas por URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job.url and job.url not in seen_urls:
                seen_urls.add(job.url)
                unique_jobs.append(job)
            elif not job.url:  # Jobs sem URL, usar outros critérios
                unique_jobs.append(job)
        
        # Analisar skills
        descriptions = [job.desc for job in unique_jobs if job.desc]
        skills_agg = aggregate_descriptions(descriptions) if descriptions else {"dev": [], "cloud": [], "soft": []}
        skills_top = top_n(skills_agg, 15)
        
        # Converter para dict
        jobs_data = [
            {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.desc,
                "source": job.source,
                "url": job.url
            }
            for job in unique_jobs
        ]
        
        # Salvar em CSV se solicitado
        if save_to_csv and unique_jobs:
            df_existing = load_jobs()
            df_new = pd.DataFrame(jobs_data)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            
            # Remover duplicatas por URL
            df_combined = df_combined.drop_duplicates(subset=['url'], keep='last')
            df_combined.to_csv("data/jobs.csv", index=False)
        
        return {
            "query": query,
            "location": location,
            "sources_requested": sources,
            "results_by_source": results_by_source,
            "total_jobs_found": len(unique_jobs),
            "jobs": jobs_data,
            "skills": skills_top,
            "saved_to_csv": save_to_csv and len(unique_jobs) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no scraping múltiplo: {str(e)}")

@app.get("/sources")
def get_available_sources():
    """Lista todas as fontes de scraping disponíveis"""
    return {
        "available_sources": list(SCRAPERS.keys()),
        "descriptions": {
            "indeed": "Indeed.com - Portal de empregos",
            "linkedin": "LinkedIn Jobs - Rede profissional",
            "glassdoor": "Glassdoor - Avaliações e vagas",
            "remotive": "Remotive.io - Vagas remotas",
            "getonboard": "GetOnBoard - Vagas tech"
        }
    }
