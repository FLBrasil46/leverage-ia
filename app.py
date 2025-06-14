import os
from flask import Flask, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

API_KEY = os.environ.get("TD_APIKEY", "")
BASE = "https://api.twelvedata.com"

ATIVOS = ["ITSA4.BVMF", "BBAS3.BVMF", "TAEE11.BVMF"]

def fetch_dividends_calendar(start, end):
    url = f"{BASE}/dividends_calendar?exchange=BVMF&start_date={start}&end_date={end}&apikey={API_KEY}"
    try:
        resp = requests.get(url, timeout=5)
        return resp.json().get("dividends", [])
    except Exception as e:
        print("Erro na API:", e)
        return []

@app.route("/")
def index():
    hoje = datetime.today().date()
    fim = hoje + timedelta(days=15)
    divs = fetch_dividends_calendar(hoje.isoformat(), fim.isoformat())

    ticker = request.args.get("q", "").upper()
    if ticker:
        divs = [d for d in divs if d["symbol"].startswith(ticker)]

    html = """
    <html><head><meta charset="utf-8"><title>Leverage IA - Proventos</title></head>
    <body style="font-family:sans-serif;padding:20px">
      <h1>Próximos proventos (15 dias)</h1>
      <form><input name="q" placeholder="Ativo (ex: ITSA4)" value="{t}"><button>Filtrar</button></form>
      <table border="1" cellpadding="5" style="border-collapse:collapse;margin-top:20px;">
        <tr><th>Ativo</th><th>Data</th><th>Valor</th></tr>
    """.format(t=ticker)

    if divs:
        for d in divs:
            if d["symbol"] in ATIVOS:
                html += f"<tr><td>{d['symbol']}</td><td>{d['ex_date']}</td><td>{d['dividend']}</td></tr>"
    else:
        html += "<tr><td colspan='3'>Nenhum provento encontrado</td></tr>"

    html += "</table></body></html>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
