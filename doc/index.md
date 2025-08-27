# Busca Vagas — Visão Geral

Este projeto coleta vagas de emprego de fontes públicas, analisa descrições para extrair hard e soft skills e disponibiliza resultados via:
- Dashboard interativo (Streamlit) em `app.py`.
- API (FastAPI) em `api.py`.
- CSV consolidado em `data/jobs.csv`.

Fontes atuais
- Remotive (API pública)
- Get On Board (API pública)
- LinkedIn  
- Indeed e Glassdoor  

Principais componentes
- `src/scrapers/`: scrapers e modelos (`Job`).
- `src/skills/`: léxico e analisador de skills.
- `collect_and_analyze.py`: CLI para coletar, deduplicar, analisar e exportar.
- `app.py`: dashboard Streamlit com gráficos de Top skills.
- `api.py`: endpoints REST para obter Top skills filtradas.
- `data/`: CSVs e arquivos de debug.

Quickstart
1) Instalar dependências (com venv):
```bash
venv/bin/python -m pip install -r requirements.txt
```
2) Coletar e gerar `data/jobs.csv` (ex.: fontes sem bloqueio):
```bash
venv/bin/python collect_and_analyze.py "front end junior" --sources getonboard remotive --limit 120
```
3) Rodar dashboard:
```bash
venv/bin/streamlit run app.py
```
4) Subir API:
```bash
venv/bin/uvicorn api:app --reload
```

Dicas
- Para LinkedIn, crie `data/linkedin_jobs.csv` (colunas: title,company,location,desc,url) e rode:
```bash
venv/bin/python collect_and_analyze.py "front end junior" --sources linkedin --limit 50
```
- Ajuste léxico/aliases em `src/skills/lexicon.py`.