from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

url = "https://br.indeed.com/jobs?q=front+end+junior&l=Brasil"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # headless=False abre janela do navegador
    page = browser.new_page()
    page.goto(url, timeout=60000)

    # Espera o JS carregar
    page.wait_for_timeout(5000)

    # Pega o HTML já processado
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    jobs = []
    for card in soup.select("a.tapItem"):
        title = card.select_one("h2.jobTitle")
        company = card.select_one("span.companyName")
        location = card.select_one("div.companyLocation")
        desc = card.select_one("div.job-snippet")

        jobs.append({
            "title": title.get_text(strip=True) if title else "N/A",
            "company": company.get_text(strip=True) if company else "N/A",
            "location": location.get_text(strip=True) if location else "N/A",
            "desc": desc.get_text(" ", strip=True) if desc else ""
        })

    browser.close()

# Mostra as primeiras vagas
for job in jobs[:5]:
    print("Título:", job["title"])
    print("Empresa:", job["company"])
    print("Local:", job["location"])
    print("Descrição:", job["desc"])
    print("-" * 40)
