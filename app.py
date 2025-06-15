import os
import requests
from flask import Flask
import json

app = Flask(__name__)

API_KEY = os.environ.get("MARKETSTACK_API_KEY", "")  # Defina no Render
HEADERS = {"apikey": API_KEY}
BASE_URL = "http://api.marketstack.com/v1"

TICKERS = ["AAPL", "MSFT", "KO", "PG", "PEP", "JNJ", "XOM", "TSLA"]

def get_dividends(ticker):
    url = f"{BASE_URL}/dividends?access_key={API_KEY}&symbols={ticker}&limit=5"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print("Erro:", e)
        return []

@app.route("/")
def index():
    rows = ""
    chart_labels = []
    chart_values = []

    for ticker in TICKERS:
        dividendos = get_dividends(ticker)
        for d in dividendos:
            rows += f"<tr><td>{ticker}</td><td>{d.get('date','')}</td><td>{d.get('dividend','')}</td></tr>"
            chart_labels.append(d.get('date'))
            chart_values.append(d.get('dividend'))

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Leverage IA - Dividendos</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-light p-4">
        <div class="container">
            <h1 class="mb-4">📈 Leverage IA - Dividendos Recentes</h1>
            <table class="table table-striped table-bordered">
                <thead class="table-dark"><tr><th>Ativo</th><th>Data</th><th>Valor</th></tr></thead>
                <tbody>{rows or "<tr><td colspan='3'>Nenhum dado encontrado</td></tr>"}</tbody>
            </table>
            <canvas id="grafico" height="100"></canvas>
        </div>
        <script>
        const ctx = document.getElementById('grafico').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(chart_labels)},
                datasets: [{{
                    label: 'Dividendos por data',
                    data: {json.dumps(chart_values)},
                    backgroundColor: 'rgba(54, 162, 235, 0.6)'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'top' }},
                    title: {{
                        display: true,
                        text: 'Histórico de Proventos'
                    }}
                }}
            }}
        }});
        </script>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
