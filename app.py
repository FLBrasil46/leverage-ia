import os
import requests
from flask import Flask, request
from datetime import datetime
import json

app = Flask(__name__)

BRAPI_TOKEN = os.environ.get("BRAPI_TOKEN", "")  # configure no Render
HEADERS = {"Authorization": f"Bearer {BRAPI_TOKEN}"} if BRAPI_TOKEN else {}

def get_dividendos(ticker):
    url = f"https://brapi.dev/api/quote/{ticker}?modules=dividends"
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        dividendos = data["results"][0].get("dividendsData", {}).get("dividends", [])
        return dividendos
    except Exception as e:
        print(f"Erro: {e}")
        return []

@app.route("/")
def index():
    ticker = request.args.get("q", "ITSA4").upper()
    setor = request.args.get("setor", "Bancos")

    dividendos = get_dividendos(ticker)
    rows = ""
    for d in dividendos:
        rows += f"<tr><td>{d.get('paymentDate')}</td><td>{d.get('label')}</td><td>{d.get('value')}</td></tr>"

    labels = [f'"{d.get("paymentDate")}"' for d in dividendos]
    values = [d.get("value", 0) for d in dividendos]

    html = f"""
    <html><head><meta charset="utf-8"><title>LEVERAGE IA</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script></head>
    <body style="font-family: sans-serif; padding: 20px">
        <h1>LEVERAGE IA</h1>
        <form>
            <input name="q" placeholder="Digite o ticker" value="{ticker}">
            <select name="setor">
                <option value="Bancos" {"selected" if setor == "Bancos" else ""}>Bancos</option>
                <option value="Elétrico" {"selected" if setor == "Elétrico" else ""}>Elétrico</option>
                <option value="FIIs" {"selected" if setor == "FIIs" else ""}>FIIs</option>
            </select>
            <button type="submit">Buscar</button>
        </form>
        <h2>Dividendos de {ticker}</h2>
        <table border="1" cellpadding="5" style="border-collapse: collapse; margin-top: 10px;">
            <tr><th>Data</th><th>Tipo</th><th>Valor</th></tr>
            {rows if rows else "<tr><td colspan='3'>Sem dados</td></tr>"}
        </table>
        <canvas id="grafico" width="400" height="150" style="margin-top: 20px;"></canvas>
        <script>
        new Chart(document.getElementById("grafico"), {{
            type: "bar",
            data: {{
                labels: [{",".join(labels)}],
                datasets: [{{
                    label: "Proventos",
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
