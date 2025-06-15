from flask import Flask
import json
import os

app = Flask(__name__)

# Dados simulados de dividendos (você pode trocar por chamada real depois)
dividendos = [
    {"ticker": "AAPL", "data_com": "2024-05-10", "pagamento": "2024-05-16", "valor": 0.26},
    {"ticker": "MSFT", "data_com": "2024-04-18", "pagamento": "2024-06-08", "valor": 0.68},
    {"ticker": "JNJ",  "data_com": "2024-05-22", "pagamento": "2024-06-04", "valor": 1.19},
    {"ticker": "KO",   "data_com": "2024-06-01", "pagamento": "2024-06-15", "valor": 0.46},
]

@app.route("/")
def index():
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
    <title>Leverage IA - Proventos</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head><body class="bg-light p-4">
    <div class="container">
        <h1 class="mb-4 text-primary">Dividendos Programados (EUA)</h1>
        <table class="table table-bordered table-striped shadow-sm">
            <thead class="table-dark">
                <tr><th>Ativo</th><th>Data Com</th><th>Pagamento</th><th>Valor (USD)</th></tr>
            </thead>
            <tbody>{rows}</tbody>
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
