# Skill Issue

Projeto para coletar vagas (Indeed na v1) e analisar as skills mais pedidas (stacks dev, cloud/devops e soft skills)
## Como rodar

1) Ambiente e dependências
- Python 3.10+
- Instalar deps
```
pip install -r requirements.txt
python -m playwright install chromium
```

2) Coleta + análise (gera data/jobs.csv)
```
python  collect_and_analyze.py "front end junior" --sources getonboard remotive --limit 120
```
 