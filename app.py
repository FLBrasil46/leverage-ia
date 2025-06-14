import os
import requests
from flask import Flask, request
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Token BRAPI configurado como variável de ambiente no Render
BRAPI_TOKEN = os.environ.get("BRAPI_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {BRAPI_TOKEN}"} if BRAPI_TOKEN else {}

def get_dividendos(ticker):
    url = f"https://brapi.dev/api/quote/{ticker}?dividends=true"
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        dividendos = data["results"][0].get("dividendsData", {}).get("dividends", [])
        return dividendos
    except Exception as e:
        print(f"Erro ao buscar dividendos: {e}")
        return []

@app.route("/")
def index():
    ticker = request.args.get("q", "ITSA4").upper()
    setor = request.args.get("setor", "Bancos")

    dividendos = get_dividendos(ticker)

    hoje = datetime.now().date()
    fim = hoje + timedelta(days=15)
    proximos = [
        d for d in dividendos
        if d.get("paymentDate") and hoje <= datetime.strptime(d["paymentDate"], "%Y-%m-%d").date() <= fim
    ]

    rows = ""
    for d in proximos:
        rows += f"<tr><td>{d.get('paymentDate')}</td><td>{d.get('label')}</td><td>{d.get('value')}</td></tr>"

    labels = [f'"{d.get("paymentDate")}"' for d in proximos]
    values = [d.get("value", 0) for d in proximos]

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
        <h2>Proventos nos próximos 15 dias ({ticker})</h2>
        <table border="1" cellpadding="5" style="border-collapse: collapse; margin-top: 10px;">
            <tr><th>Data</th><th>Tipo</th><th>Valor</th></tr>
            {rows if rows else "<tr><td colspan='3'>Sem dados próximos</td></tr>"}
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
