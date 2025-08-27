# Guia para Assistentes de IA

Este arquivo orienta um agente/IA sobre como contribuir neste projeto.

## Contexto do Projeto
- Objetivo: coletar vagas, consolidar em CSV e analisar skills (dev/cloud/soft) para insights.
- Entradas: query, location, limit, fontes.
- Saídas: `data/jobs.csv` e endpoints na FastAPI.

## Boas Práticas
- Sempre deduplique vagas por URL ou (title, company, location) antes de salvar.
- Valide mudanças com uma execução rápida do CLI e do dashboard.
- Ao alterar comportamento público, atualize README e `doc/index.md`.

## Tarefas recorrentes úteis
- Melhorar cobertura do léxico e normalização (acentos, hífens, sinônimos).
- Adicionar filtros extras (senioridade, remoto/presencial) na API `/skills`.
- Evoluir persistência para SQLite/Parquet e indexar por data de coleta.
- Criar testes unitários para `src/skills/analyzer.py`.

## Comandos úteis (venv local)
- Coletar:
```bash
venv/bin/python collect_and_analyze.py "front end junior" --sources getonboard remotive --limit 120
```
- Importar LinkedIn CSV:
```bash
venv/bin/python import_linkedin_csv.py data/linkedin_jobs.csv --out data/jobs.csv
```
- Dashboard:
```bash
venv/bin/streamlit run app.py
```
- API:
```bash
venv/bin/uvicorn api:app --reload
```
