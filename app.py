import time
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

@app.route("/")
def index():
    # Configurar navegador headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://statusinvest.com.br/proventos")

    try:
        # Espera a tabela carregar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "results"))
        )

        # Coleta os dados da tabela
        linhas = driver.find_elements(By.CSS_SELECTOR, "#results tbody tr")
        dados = []
        for linha in linhas[:30]:  # Limita para não pesar muito
            colunas = linha.find_elements(By.TAG_NAME, "td")
            if len(colunas) >= 6:
                dados.append({
                    "ativo": colunas[0].text,
                    "tipo": colunas[1].text,
                    "data_com": colunas[2].text,
                    "pagamento": colunas[3].text,
                    "valor": colunas[4].text,
                    "yield": colunas[5].text,
                })
    except Exception as e:
        driver.quit()
        return f"Erro ao extrair dados: {e}"

    driver.quit()

    # Gera HTML
    html = """
    <html><head><meta charset='utf-8'><title>Proventos - StatusInvest</title></head><body>
    <h1>Proventos Fututos</h1>
    <table border='1' cellpadding='5' cellspacing='0'>
        <tr><th>Ativo</th><th>Tipo</th><th>Data Com</th><th>Pagamento</th><th>Valor</th><th>Yield</th></tr>
    """
    for d in dados:
        html += f"<tr><td>{d['ativo']}</td><td>{d['tipo']}</td><td>{d['data_com']}</td><td>{d['pagamento']}</td><td>{d['valor']}</td><td>{d['yield']}</td></tr>"
    html += "</table></body></html>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
