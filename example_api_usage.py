#!/usr/bin/env python3
"""
Exemplos de uso da API de Scraping de Vagas

Para usar este script:
1. Inicie a API: uvicorn api:app --reload
2. Execute este script: python example_api_usage.py
"""

import requests
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def print_response(response: requests.Response, title: str):
    """Imprime resposta da API de forma formatada"""
    print(f"\n{'='*50}")
    print(f"📡 {title}")
    print(f"{'='*50}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        
        # Se for resposta de scraping, mostrar resumo
        if "jobs_found" in data:
            print(f"📊 Vagas encontradas: {data['jobs_found']}")
            
            if "skills" in data and data["skills"]:
                print(f"\n🔧 Top Tecnologias:")
                for tech, count in data["skills"].get("dev", [])[:5]:
                    print(f"   • {tech}: {count}x")
                
                print(f"\n☁️  Top Cloud/DevOps:")
                for cloud, count in data["skills"].get("cloud", [])[:5]:
                    print(f"   • {cloud}: {count}x")
                
                print(f"\n💼 Top Soft Skills:")
                for soft, count in data["skills"].get("soft", [])[:5]:
                    print(f"   • {soft}: {count}x")
            
            if "jobs" in data and data["jobs"]:
                print(f"\n📝 Primeiras 3 vagas:")
                for i, job in enumerate(data["jobs"][:3], 1):
                    print(f"   {i}. {job['title']} - {job['company']}")
        
        # Se for múltiplas fontes, mostrar resultado por fonte
        elif "results_by_source" in data:
            print(f"📊 Total de vagas: {data['total_jobs_found']}")
            print(f"\n📈 Resultados por fonte:")
            for source, result in data["results_by_source"].items():
                status = "✅" if result["success"] else "❌"
                print(f"   {status} {source}: {result['jobs_found']} vagas")
                if not result["success"]:
                    print(f"      Erro: {result['error']}")
        
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"Erro: {response.text}")

def test_health():
    """Testa se a API está funcionando"""
    response = requests.get(f"{API_BASE_URL}/health")
    print_response(response, "Health Check")

def test_get_sources():
    """Lista fontes disponíveis"""
    response = requests.get(f"{API_BASE_URL}/sources")
    print_response(response, "Fontes Disponíveis")

def test_single_scraping():
    """Testa scraping de uma fonte específica"""
    params = {
        "query": "desenvolvedor python junior",
        "location": "Brasil",
        "limit": 5,
        "save_to_csv": True
    }
    
    # Testa com fonte que provavelmente funciona (remotive)
    response = requests.post(f"{API_BASE_URL}/scrape/remotive", params=params)
    print_response(response, "Scraping Remotive - Python Junior")

def test_multiple_scraping():
    """Testa scraping de múltiplas fontes"""
    params = {
        "query": "react frontend",
        "location": "Brasil", 
        "limit": 3,
        "sources": ["remotive", "getonboard"],
        "save_to_csv": True
    }
    
    response = requests.post(f"{API_BASE_URL}/scrape/multiple", params=params)
    print_response(response, "Scraping Múltiplo - React Frontend")

def test_get_skills():
    """Testa endpoint de análise de skills"""
    params = {
        "q": "react",
        "top": 10
    }
    
    response = requests.get(f"{API_BASE_URL}/skills", params=params)
    print_response(response, "Análise de Skills - React")

def main():
    """Executa todos os testes"""
    print("🚀 Testando API de Scraping de Vagas")
    print("📝 Certifique-se de que a API está rodando: uvicorn api:app --reload")
    
    try:
        # 1. Verifica se API está online
        test_health()
        
        # 2. Lista fontes disponíveis
        test_get_sources()
        
        # 3. Testa scraping de fonte única
        test_single_scraping()
        
        # 4. Testa scraping múltiplo
        test_multiple_scraping()
        
        # 5. Testa análise de skills
        test_get_skills()
        
        print(f"\n{'='*50}")
        print("✅ Todos os testes concluídos!")
        print("📁 Verifique o arquivo data/jobs.csv para os resultados salvos")
        print(f"{'='*50}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro: Não foi possível conectar à API")
        print("💡 Certifique-se de que a API está rodando:")
        print("   uvicorn api:app --reload")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
