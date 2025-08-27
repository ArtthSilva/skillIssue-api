# Arquitetura

## Objetivo
Coletar vagas de múltiplas fontes, consolidar em CSV, analisar descrições para extrair skills (dev/cloud/soft) e expor insights via Dashboard e API.

## Módulos
- Coleta (`src/scrapers/*`): implementa `BaseScraper.search(query, location, limit)` e retorna lista de `Job`.
- Agregação/CLI (`collect_and_analyze.py`): orquestra fontes, deduplica, exporta CSV e imprime Top skills.
- Análise (`src/skills/*`): tokenização, léxico, aliases e contagem por categoria.
- Dashboard (`app.py`): carrega CSV, agrega e plota gráficos.
- API (`api.py`): endpoints REST para skills com filtros.

## Fluxo
1. Entrada: query, location, limit, sources.
2. Scrapers consultam APIs ou CSV local, retornam `Job`.
3. Deduplicação por URL ou (title, company, location).
4. Persistência em `data/jobs.csv`.
5. Análise: `aggregate_descriptions` + `top_n` usando `lexicon`.
6. Consumo: Streamlit e FastAPI.

## Decisões
- Léxico configurável em `src/skills/lexicon.py`.
- CSV como formato canônico simples (pode evoluir para SQLite/Parquet).

## Extensões futuras
- Paginação, filtros por senioridade e remoto/presencial.
- Limpeza de HTML nas descrições.
- Cache e agendamento (cron) de coletas.
- Testes automatizados (unit/integrados) para analisador e scrapers.
