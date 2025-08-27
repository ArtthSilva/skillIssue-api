import os
import csv
import logging
import re
from typing import List
from datetime import datetime
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters, OnSiteOrRemoteFilters
from src.scrapers.models import Job
from src.skills.analyzer import classify_tokens

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Lista para armazenar os jobs encontrados
jobs_found: List[Job] = []

def extract_relevant_skills(desc: str) -> str:
    """Extrai apenas as tecnologias, cloud e soft skills relevantes da descrição"""
    if not desc:
        return "N/A"
    
    # Remove HTML tags se existirem
    desc = re.sub(r'<[^>]+>', '', desc)
    
    # Usar o analisador para classificar tokens
    skills_found = classify_tokens(desc)
    
    # Construir texto resumido com apenas as skills encontradas
    relevant_parts = []
    
    # Adicionar tecnologias de desenvolvimento
    if skills_found["dev"]:
        dev_skills = list(skills_found["dev"].keys())
        relevant_parts.append(f"Tecnologias: {', '.join(dev_skills)}")
    
    # Adicionar tecnologias cloud
    if skills_found["cloud"]:
        cloud_skills = list(skills_found["cloud"].keys())
        relevant_parts.append(f"Cloud: {', '.join(cloud_skills)}")
    
    # Adicionar soft skills
    if skills_found["soft"]:
        soft_skills = list(skills_found["soft"].keys())
        relevant_parts.append(f"Soft Skills: {', '.join(soft_skills)}")
    
    # Se não encontrou nenhuma skill relevante, manter uma versão resumida da descrição original
    if not relevant_parts:
        # Pegar primeiras sentenças que podem conter informações relevantes
        sentences = desc.split('.')[:3]
        clean_desc = '. '.join(sentences).strip()
        if len(clean_desc) > 300:
            clean_desc = clean_desc[:297] + "..."
        return clean_desc
    
    return " | ".join(relevant_parts)

def on_data(data: EventData):
    # Extrair apenas informações relevantes (skills) da descrição
    relevant_skills = extract_relevant_skills(data.description)
    
    # Criar objeto Job compatível com o modelo do projeto
    job = Job(
        title=data.title or "N/A",
        company=data.company or "N/A", 
        location=data.place or "N/A",
        desc=relevant_skills,
        source="LinkedIn",
        url=data.link or None
    )
    
    # Adicionar à lista
    jobs_found.append(job)
    
    print(f"=== Vaga {len(jobs_found)} encontrada ===")
    print(f"Título: {job.title}")
    print(f"Empresa: {job.company}")
    print(f"Local: {job.location}")
    print(f"Data: {data.date}")
    print(f"Link: {job.url}")
    print(f"Skills Relevantes: {job.desc}")
    print("========================\n")

def on_metrics(metrics: EventMetrics):
    print(f"[PROGRESSO] {metrics}")

def on_error(error):
    print(f'[ERRO] {error}')

def on_end():
    print('\n' + '='*50)
    print('[FINALIZADO] Busca concluída')
    print('='*50)
    
    if jobs_found:
        print(f"\n📊 RESUMO DO SCRAPING:")
        print(f"   Total de vagas encontradas: {len(jobs_found)}")
        print(f"\n📝 VAGAS COLETADAS:")
        
        for i, job in enumerate(jobs_found, 1):
            print(f"   {i:2d}. {job.title} - {job.company}")
        
        # Mostrar empresas únicas
        empresas_unicas = set(job.company for job in jobs_found)
        print(f"\n🏢 EMPRESAS ({len(empresas_unicas)}):")
        for empresa in sorted(empresas_unicas):
            count = sum(1 for job in jobs_found if job.company == empresa)
            print(f"   • {empresa} ({count} vaga{'s' if count > 1 else ''})")
        
        # Analisar todas as descrições para extrair skills
        from src.skills.analyzer import aggregate_descriptions
        all_descriptions = [job.desc for job in jobs_found if job.desc != "N/A"]
        
        if all_descriptions:
            skills_summary = aggregate_descriptions(all_descriptions)
            
            print(f"\n🔧 TECNOLOGIAS ENCONTRADAS ({len(skills_summary['dev'])}):")
            if skills_summary['dev']:
                for tech, count in skills_summary['dev'].most_common(10):
                    print(f"   • {tech} ({count}x)")
            else:
                print("   Nenhuma tecnologia identificada")
            
            print(f"\n☁️  CLOUD/DEVOPS ENCONTRADAS ({len(skills_summary['cloud'])}):")
            if skills_summary['cloud']:
                for cloud, count in skills_summary['cloud'].most_common(10):
                    print(f"   • {cloud} ({count}x)")
            else:
                print("   Nenhuma tecnologia cloud identificada")
            
            print(f"\n💼 SOFT SKILLS ENCONTRADAS ({len(skills_summary['soft'])}):")
            if skills_summary['soft']:
                for soft, count in skills_summary['soft'].most_common(10):
                    print(f"   • {soft} ({count}x)")
            else:
                print("   Nenhuma soft skill identificada")
        
        # Salvar jobs encontrados em CSV
        csv_file = 'data/jobs.csv'
        
        # Verificar se já existe arquivo e carregar dados existentes
        existing_jobs = []
        if os.path.exists(csv_file):
            try:
                with open(csv_file, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    existing_jobs = list(reader)
            except Exception as e:
                print(f"⚠️  Aviso: Erro ao ler arquivo existente: {e}")
        
        # Combinar jobs existentes com novos
        all_jobs = existing_jobs.copy()
        existing_urls = {job.get('url') for job in existing_jobs if job.get('url')}
        
        # Adicionar apenas jobs novos (não duplicados)
        new_jobs_added = 0
        for job in jobs_found:
            if job.url not in existing_urls:
                all_jobs.append({
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'desc': job.desc,
                    'source': job.source,
                    'url': job.url
                })
                new_jobs_added += 1
        
        # Salvar arquivo consolidado
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Cabeçalho
            writer.writerow(['title', 'company', 'location', 'desc', 'source', 'url'])
            
            # Dados
            for job in all_jobs:
                if isinstance(job, dict):
                    writer.writerow([
                        job['title'],
                        job['company'],
                        job['location'],
                        job['desc'],
                        job['source'],
                        job['url']
                    ])
                else:
                    writer.writerow([
                        job.title,
                        job.company,
                        job.location,
                        job.desc,
                        job.source,
                        job.url
                    ])
        
        print(f"\n✅ {new_jobs_added} vagas novas adicionadas ao {csv_file}")
        print(f"📊 Total de vagas no arquivo: {len(all_jobs)}")
    else:
        print("❌ Nenhuma vaga encontrada para salvar")
    
    print('='*50)

# Verificar se o cookie está definido
li_at_cookie = os.getenv("LI_AT_COOKIE")
if not li_at_cookie:
    print("⚠️  ATENÇÃO: Cookie LI_AT_COOKIE não encontrado!")
    print("Para usar sessão autenticada, defina:")
    print("export LI_AT_COOKIE='seu_valor_do_cookie_li_at'")
    print("\nExecutando em modo anônimo (pode não funcionar)...")

scraper = LinkedinScraper(
    chrome_executable_path=None,
    headless=True,
    max_workers=1,
    slow_mo=1.5,  # Aumentado para evitar rate limiting
    page_load_timeout=40
)

# Registrar eventos
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)
scraper.on(Events.METRICS, on_metrics)

queries = [
    Query(
        query='"React" AND ("Front" OR "Frontend" OR "FE") AND NOT ("Pleno" OR "PL" OR "Mid" OR "Senior" OR "SR" OR "SSR" OR "BairesDev" OR "IBM" OR "Netvagas")',
        options=QueryOptions(
            locations=['Brasil'],
            limit=10,
            filters=QueryFilters(
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.WEEK,
                type=[TypeFilters.FULL_TIME],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL, ExperienceLevelFilters.INTERNSHIP],
                on_site_or_remote=[OnSiteOrRemoteFilters.ON_SITE, OnSiteOrRemoteFilters.REMOTE, OnSiteOrRemoteFilters.HYBRID]
            )
        )
    ),
    Query(
        query='Desenvolvedor Python Júnior',
        options=QueryOptions(
            locations=['Brasil'],
            limit=5,
            filters=QueryFilters(
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.WEEK,
                type=[TypeFilters.FULL_TIME],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL]
            )
        )
    )
]

scraper.run(queries)