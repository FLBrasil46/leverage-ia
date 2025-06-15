import os
import requests
from flask import Flask, request

app = Flask(__name__)

def get_dividendos(ticker):
    url = f"https://brapi.dev/api/quote/{ticker}?dividends=true"
    try:
        response = requests.get(url)
        data = response.json()
        return data['results'][0].get('dividendsData', {}).get('dividends', [])
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return []

@app.route("/")
def index():
    ticker = request.args.get("q", "ITSA4").upper()
    dividendos = get_dividendos(ticker)

    rows = ""
    for d in dividendos:
        rows += f"<tr><td>{d.get('paymentDate')}</td><td>{d.get('label')}</td><td>{d.get('value')}</td></tr>"

    html = f"""
    <html>
    <head><title>Proventos BRAPI</title></head>
    <body style="font-family:sans-serif;padding:20px;">
        <h1>Dividendos - {ticker}</h1>
        <form><input name="q" placeholder="Ticker" value="{ticker}"><button type="submit">Buscar</button></form>
        <table border="1" cellpadding="5" style="margin-top:10px;">
            <tr><th>Data Pagamento</th><th>Tipo</th><th>Valor</th></tr>
            {rows if rows else "<tr><td colspan='3'>Sem dados encontrados</td></tr>"}
        </table>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
