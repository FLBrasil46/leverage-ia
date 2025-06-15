import os
import requests
from flask import Flask
import json

app = Flask(__name__)

API_KEY = os.environ.get("MARKETSTACK_API_KEY", "")  # variável de ambiente no Render
BASE_URL = "http://api.marketstack.com/v1/dividends"

# Ativos que serão exibidos automaticamente
TICKERS = ["AAPL", "MSFT", "KO", "JNJ", "IBM", "GOOGL"]

def buscar_dividendos(ticker):
    try:
        params = {
            "access_key": API_KEY,
            "symbols": ticker,
            "limit": 5  # últimos dividendos
        }
        r = requests.get(BASE_URL, params=params)
        dados = r.json().get("data", [])
        return [{
            "ticker": ticker,
            "data_com": d.get("ex_date", "N/A"),
            "pagamento": d.get("payment_date", "N/A"),
            "valor": d.get("dividend", 0)
        } for d in dados if d.get("dividend", 0) > 0]
    except Exception as e:
        print(f"Erro ao buscar {ticker}: {e}")
        return []

@app.route("/")
def index():
    dividendos = []
    for t in TICKERS:
        dividendos += buscar_dividendos(t)

    # Ordenar por data de pagamento
    dividendos.sort(key=lambda x: x["pagamento"])

    # Construção da tabela e gráfico
    rows = ""
    labels = []
    values = []

    for d in dividendos:
        rows += f"<tr><td>{d['ticker']}</td><td>{d['data_com']}</td><td>{d['pagamento']}</td><td>{d['valor']}</td></tr>"
        labels.append(f"{d['ticker']} ({d['pagamento']})")
        values.append(d['valor'])

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-br"><head><meta charset="UTF-8">
    <title>Leverage IA - Proventos EUA</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head><body class="bg-light p-4">
    <div class="container">
        <h1 class="mb-4 text-primary">Proventos Confirmados - Ações Americanas</h1>
        <table class="table table-bordered table-striped shadow-sm">
            <thead class="table-dark">
                <tr><th>Ativo</th><th>Data Com</th><th>Pagamento</th><th>Valor (USD)</th></tr>
            </thead>
            <tbody>{rows or '<tr><td colspan=4>Sem dados</td></tr>'}</tbody>
        </table>
        <h5 class="mt-5">Distribuição gráfica</h5>
        <canvas id="grafico" height="100"></canvas>
    </div>
    <script>
        new Chart(document.getElementById("grafico"), {{
            type: "bar",
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: "Valor por Ação (USD)",
                    data: {json.dumps(values)},
                    backgroundColor: "rgba(75, 192, 192, 0.5)"
                }}]
            }}
        }});
    </script>
    </body></html>
    """
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
