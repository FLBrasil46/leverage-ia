from flask import Flask
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Leitura do arquivo HTML no diretório do projeto
DATA_FILE = "investidor10_dividendos.txt"

try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        html = f.read()
except FileNotFoundError:
    html = ""
    print(f"Arquivo não encontrado: {DATA_FILE}")

soup = BeautifulSoup(html, "html.parser")
tabela = soup.find("table")
proventos = []

if tabela:
    for row in tabela.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) >= 5:
            proventos.append({
                "ticker": cols[0].text.strip(),
                "tipo": cols[1].text.strip(),
                "data_com": cols[2].text.strip(),
                "pagamento": cols[3].text.strip(),
                "valor": cols[4].text.strip(),
            })

@app.route("/")
def index():
    if not proventos:
        return "<h2>Nenhum dado carregado. Verifique o arquivo investidor10_dividendos.txt</h2>"

    linhas = "".join([
        f"<tr><td>{p['ticker']}</td><td>{p['tipo']}</td><td>{p['data_com']}</td><td>{p['pagamento']}</td><td>{p['valor']}</td></tr>"
        for p in proventos
    ])

    html = f"""
    <!DOCTYPE html><html><head><meta charset='utf-8'>
    <title>Proventos - Investidor10</title>
    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css' rel='stylesheet'>
    </head><body class='container py-4'>
    <h1 class='mb-4'>LEVERAGE IA - MELHORES OPORTUNIDADES</h1>
    <table class='table table-bordered table-striped'>
        <thead class='table-dark'><tr>
            <th>Ticker</th><th>Tipo</th><th>Data COM</th><th>Pagamento</th><th>Valor</th>
        </tr></thead><tbody>{linhas}</tbody>
    </table>
    </body></html>
    """
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
