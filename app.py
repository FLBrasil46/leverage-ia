import os
import requests
from flask import Flask
from datetime import datetime

app = Flask(__name__)
API_KEY = os.environ.get("MARKETSTACK_KEY", "")
BASE = "https://api.marketstack.com/v1"
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "JNJ", "KO", "PG", "PFE", "NVDA"]

def fetch_dividends(symbol):
    params = {"access_key": API_KEY, "symbols": symbol, "limit": 100}
    try:
        r = requests.get(f"{BASE}/dividends", params=params, timeout=5)
        return r.json().get("data", [])
    except Exception as e:
        print(f"Erro ao buscar {symbol}: {e}")
        return []

@app.route("/")
def index():
    html_rows = ""
    for t in TICKERS:
        divs = fetch_dividends(t)
        for d in divs:
            date = d.get("date", "—")[:10]
            amount = d.get("dividend", 0)
            html_rows += f"<tr><td>{t}</td><td>{date}</td><td>{amount:.4f}</td></tr>"

    html = f"""
    <html><head><meta charset="utf-8"><title>Dividendos</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    </head><body class="p-4">
      <h2>Dividendos encontrados</h2>
      <table class="table table-striped">
        <thead><tr><th>Ativo</th><th>Data</th><th>Valor</th></tr></thead>
        <tbody>
          {html_rows or '<tr><td colspan="3">Nenhum dividendo encontrado.</td></tr>'}
        </tbody>
      </table>
      <p class="text-muted">Dados via Marketstack (<a href="https://marketstack.com/">API</a>)</p>
    </body></html>
    """
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
