import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import json

app = Flask(__name__)

def coletar_preco_alvo_walletinvestor(ticker):
    url = f"https://walletinvestor.com/analytic/{ticker}-forecast"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        card = soup.find("div", class_="card-body")
        target = None
        if card:
            span = card.find("span", text=lambda t: t and "Target mean" in t)
            if span:
                val = span.find_next("span").get_text(strip=True).replace(',', '')
                target = float(val)
        return target
    except Exception as e:
        print(f"Erro ao buscar dados de {ticker}: {e}")
        return None

@app.route("/")
def index():
    ticker = request.args.get("q", "PETR4").upper()
    precos_alvo = []

    target = coletar_preco_alvo_walletinvestor(ticker)
    if target:
        precos_alvo.append({"fonte": "WalletInvestor", "valor": target})

    labels = [p["fonte"] for p in precos_alvo]
    valores = [p["valor"] for p in precos_alvo]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Preço-Alvo - {ticker}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="container py-4">
        <h1 class="mb-4">Preço-Alvo Médio de <strong>{ticker}</strong></h1>
        <form class="mb-3">
            <input type="text" name="q" value="{ticker}" placeholder="Ex: PETR4" class="form-control w-25 d-inline">
            <button type="submit" class="btn btn-primary">Buscar</button>
        </form>

        <table class="table table-bordered">
            <thead><tr><th>Fonte</th><th>Preço-Alvo</th></tr></thead>
            <tbody>
                {''.join(f"<tr><td>{p['fonte']}</td><td>R$ {p['valor']:.2f}</td></tr>" for p in precos_alvo) if precos_alvo else '<tr><td colspan="2">Nenhum dado encontrado</td></tr>'}
            </tbody>
        </table>

        <canvas id="grafico" width="400" height="150" class="mt-4"></canvas>
        <script>
            new Chart(document.getElementById("grafico"), {{
                type: "bar",
                data: {{
                    labels: {json.dumps(labels)},
                    datasets: [{{
                        label: "Preço-Alvo (R$)",
                        data: {json.dumps(valores)},
                        backgroundColor: "rgba(54, 162, 235, 0.6)"
                    }}]
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
