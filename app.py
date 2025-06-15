from flask import Flask, request
import statistics
import json

app = Flask(__name__)

# Simulação de fontes públicas
def coletar_precos_alvo(ticker):
    # Em uma versão com scraping real, usaríamos requests + BeautifulSoup aqui
    fontes = {
        "XP Investimentos": 34.50,
        "BTG Pactual": 36.00,
        "Itaú BBA": 35.20,
        "Bradesco BBI": 33.90,
        "Genial Investimentos": 36.50,
        "Empiricus": 34.75,
        "Modalmais": 35.10,
    }
    return fontes

@app.route("/")
def index():
    ticker = request.args.get("q", "PETR4").upper()
    precos = coletar_precos_alvo(ticker)

    media = round(statistics.mean(precos.values()), 2) if precos else 0.0

    linhas = ""
    for fonte, preco in precos.items():
        linhas += f"<tr><td>{fonte}</td><td>R$ {preco:.2f}</td></tr>"

    fontes = [f'"{fonte}"' for fonte in precos.keys()]
    valores = list(precos.values())

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Preço-Alvo: {ticker}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="container py-4">
        <h1 class="mb-4">Preço-Alvo: {ticker}</h1>
        <form method="get" class="mb-3">
            <input name="q" value="{ticker}" class="form-control" placeholder="Digite o ticker" style="max-width: 300px; display: inline-block;">
            <button type="submit" class="btn btn-primary">Buscar</button>
        </form>

        <h3>Média dos Preços-Alvo: R$ {media:.2f}</h3>

        <table class="table table-bordered mt-3">
            <thead><tr><th>Fonte</th><th>Preço-Alvo</th></tr></thead>
            <tbody>{linhas}</tbody>
        </table>

        <canvas id="grafico" height="100"></canvas>
        <script>
        new Chart(document.getElementById("grafico"), {{
            type: "bar",
            data: {{
                labels: [{','.join(fontes)}],
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
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
