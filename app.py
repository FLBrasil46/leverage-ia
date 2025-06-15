import os
import requests
from bs4 import BeautifulSoup
from flask import Flask
from datetime import datetime

app = Flask(__name__)

def obter_proventos():
    url = "https://investidor10.com.br/proventos/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        tabela = soup.find("table")
        linhas = tabela.find("tbody").find_all("tr")
        proventos = []

        for linha in linhas:
            colunas = linha.find_all("td")
            if len(colunas) < 6:
                continue
            papel = colunas[0].text.strip()
            tipo = colunas[1].text.strip()
            data_com = colunas[2].text.strip()
            pagamento = colunas[3].text.strip()
            valor = colunas[4].text.strip()
            proventos.append({
                "papel": papel,
                "tipo": tipo,
                "data_com": data_com,
                "pagamento": pagamento,
                "valor": valor
            })
        return proventos
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return []

@app.route("/")
def index():
    proventos = obter_proventos()
    linhas = ""
    for p in proventos:
        linhas += f"""
        <tr>
            <td>{p['papel']}</td>
            <td>{p['tipo']}</td>
            <td>{p['data_com']}</td>
            <td>{p['pagamento']}</td>
            <td>{p['valor']}</td>
        </tr>
        """

    html = f"""
    <html><head><meta charset="utf-8">
    <title>Dividendos</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head><body class="p-4">
        <h1 class="mb-4">Proventos Futuros (Investidor10)</h1>
        <table class="table table-bordered table-striped">
            <thead><tr>
                <th>Papel</th><th>Tipo</th><th>Data COM</th><th>Pagamento</th><th>Valor</th>
            </tr></thead>
            <tbody>
                {linhas if linhas else "<tr><td colspan='5'>Sem dados disponíveis</td></tr>"}
            </tbody>
        </table>
    </body></html>
    """
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
