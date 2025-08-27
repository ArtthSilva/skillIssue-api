# Skill Issue - Back
Projeto para coletar vagas de emprego em sites como LinkedIn, GetOnBoard e Remotive e analisar as skills mais pedidas (stacks de desenvolvimento, cloud/devops e soft skills).
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
 
