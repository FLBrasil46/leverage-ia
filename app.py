import os
import requests
from flask import Flask
from datetime import datetime
import json

app = Flask(__name__)

API_KEY = os.environ.get("MARKETSTACK_API_KEY", "")
BASE_URL = "http://api.marketstack.com/v1/dividends"

# Ativos americanos populares para exemplo
TICKERS = ["AAPL", "MSFT", "KO", "JNJ", "IBM", "PEP", "PG", "MO", "INTC", "T"]

def formatar_data(data_iso):
    try:
        return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return "—"

def buscar_dividendos_marketstack(ticker):
    try:
        params = {
            "access_key": API_KEY,
            "symbols": ticker,
            "limit": 5
        }
        response = requests.get(BASE_URL, params=params)
        dados = response.json().get("data", [])
        return [{
            "ticker": ticker,
            "data_com": formatar_data(d.get("ex_date")),
            "pagamento": formatar_data(d.get("payment_date")),
            "valor": d.get("dividend", 0)
        } for d in dados if d.get("dividend")]
    except Exception as e:
        print(f"Erro ao buscar {ticker}: {e}")
        return []

@app.route("/")
def index():
    dividendos = []
    for t in TICKERS:
        dividendos += buscar_dividendos_marketstack(t)

    dividendos.sort(key=lambda x: x["pagamento"])

    rows = ""
    labels = []
    values = []

    for d in dividendos:
        rows += f"<tr><td>{d['ticker']}</td><td>{d['data_com']}</td><td>{d['pagamento']}</td><td>{d['valor']:.2f}</td></tr>"
        labels.append(f"{d['ticker']} ({d['pagamento']})")
        values.append(d['valor'])

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-br"><head><meta charset="UTF-8">
    <title>Leverage IA - Dividendos</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head><body class="bg-light p-4">
    <div class="container">
        <h1 class="mb-4 text-primary">Dividendos Confirmados (Ações EUA)</h1>
        <table class="table table-bordered table-striped shadow-sm">
            <thead class="table-dark">
                <tr><th>Ativo</th><th>Data Com</th><th>Pagamento</th><th>Valor (USD)</th></tr>
            </thead>
            <tbody>{rows or '<tr><td colspan=4>Sem dados disponíveis</td></tr>'}</tbody>
        </table>
        <h5 class="mt-5">Distribuição Gráfica</h5>
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
                    backgroundColor: "rgba(54, 162, 235, 0.5)"
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
