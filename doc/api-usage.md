# API de Scraping de Vagas - Guia de Uso

## Como iniciar a API

```bash
# No diretório do projeto
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

## Endpoints Disponíveis

### 1. Health Check
Verifica se a API está funcionando.

```bash
curl "http://localhost:8000/health"
```

**Resposta:**
```json
{"status": "ok"}
```

### 2. Listar Fontes Disponíveis
Lista todas as fontes de scraping.

```bash
curl "http://localhost:8000/sources"
```

**Resposta:**
```json
{
  "available_sources": ["indeed", "linkedin", "glassdoor", "remotive", "getonboard"],
  "descriptions": {
    "indeed": "Indeed.com - Portal de empregos",
    "linkedin": "LinkedIn Jobs - Rede profissional",
    "glassdoor": "Glassdoor - Avaliações e vagas",
    "remotive": "Remotive.io - Vagas remotas",
    "getonboard": "GetOnBoard - Vagas tech"
  }
}
```

### 3. Scraping de Fonte Única
Executa scraping de uma fonte específica.

```bash
curl -X POST "http://localhost:8000/scrape/remotive?query=python%20developer&location=Brasil&limit=10&save_to_csv=true"
```

**Parâmetros:**
- `query`: Termo de busca (obrigatório)
- `location`: Localização (padrão: "Brasil")
- `limit`: Limite de vagas (1-100, padrão: 20)
- `save_to_csv`: Salvar em CSV (true/false, padrão: true)

**Exemplo de resposta:**
```json
{
  "source": "remotive",
  "query": "python developer",
  "location": "Brasil",
  "jobs_found": 5,
  "jobs": [
    {
      "title": "Python Developer",
      "company": "Tech Corp",
      "location": "Remote",
      "description": "Tecnologias: python, django, postgresql",
      "source": "remotive",
      "url": "https://example.com/job/123"
    }
  ],
  "skills": {
    "dev": [["python", 3], ["django", 2]],
    "cloud": [["aws", 1]],
    "soft": [["teamwork", 2]]
  },
  "saved_to_csv": true
}
```

### 4. Scraping de Múltiplas Fontes
Executa scraping de várias fontes em paralelo.

```bash
curl -X POST "http://localhost:8000/scrape/multiple" \
  -G \
  -d "query=react frontend" \
  -d "location=Brasil" \
  -d "limit=5" \
  -d "sources=remotive" \
  -d "sources=getonboard" \
  -d "save_to_csv=true"
```

**Exemplo de resposta:**
```json
{
  "query": "react frontend",
  "location": "Brasil",
  "sources_requested": ["remotive", "getonboard"],
  "results_by_source": {
    "remotive": {"jobs_found": 3, "success": true, "error": null},
    "getonboard": {"jobs_found": 2, "success": true, "error": null}
  },
  "total_jobs_found": 5,
  "jobs": [...],
  "skills": {...},
  "saved_to_csv": true
}
```

### 5. Análise de Skills
Analisa skills das vagas já coletadas no arquivo CSV.

```bash
curl "http://localhost:8000/skills?q=react&location=remoto&top=15"
```

**Parâmetros:**
- `q`: Filtro por texto no título/descrição (opcional)
- `location`: Filtro por localização (opcional)
- `source`: Filtro por fonte (opcional)
- `top`: Quantidade de items por categoria (1-50, padrão: 10)

## Exemplos Práticos

### 1. Coletar vagas de Python júnior do Remotive
```bash
curl -X POST "http://localhost:8000/scrape/remotive?query=python%20junior&limit=10"
```

### 2. Coletar vagas de React de múltiplas fontes
```bash
curl -X POST "http://localhost:8000/scrape/multiple" \
  -G \
  -d "query=react developer" \
  -d "limit=5" \
  -d "sources=remotive" \
  -d "sources=getonboard"
```

### 3. Analisar skills de vagas remotas
```bash
curl "http://localhost:8000/skills?location=remote&top=20"
```

### 4. Buscar vagas específicas e analisar
```bash
# Primeiro, coletar vagas
curl -X POST "http://localhost:8000/scrape/multiple" \
  -G \
  -d "query=fullstack javascript" \
  -d "sources=remotive" \
  -d "sources=getonboard"

# Depois, analisar skills das vagas coletadas
curl "http://localhost:8000/skills?q=javascript&top=15"
```

## Fontes Recomendadas

### Sem bloqueio (funcionam bem):
- `remotive`: Vagas remotas internacionais
- `getonboard`: Vagas tech da América Latina

### Com possível bloqueio:
- `indeed`: Pode ter rate limiting
- `linkedin`: Requer autenticação
- `glassdoor`: Pode ter captcha

## Dicas de Uso

1. **Comece com fontes confiáveis**: Use `remotive` e `getonboard` primeiro
2. **Limites baixos**: Use `limit=5-10` para testes, `limit=20-50` para coletas reais
3. **Salve em CSV**: Use `save_to_csv=true` para acumular dados
4. **Analise depois**: Use `/skills` para analisar os dados coletados
5. **Queries específicas**: Use termos como "python junior", "react frontend", "devops"

## Tratamento de Erros

A API retorna diferentes códigos de status:
- `200`: Sucesso
- `400`: Parâmetros inválidos ou fonte não disponível
- `500`: Erro interno (scraper falhou, timeout, etc.)

Exemplo de erro:
```json
{
  "detail": "Fonte 'invalid' não disponível. Fontes: ['indeed', 'linkedin', 'glassdoor', 'remotive', 'getonboard']"
}
```

## Monitoramento

Para ver logs em tempo real:
```bash
tail -f logs/api.log  # Se configurado logging em arquivo
```

Ou observe o terminal onde a API está rodando para ver as mensagens de debug.
