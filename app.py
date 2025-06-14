import os
import requests
from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)

BRAPI_TOKEN = os.environ.get("BRAPI_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {BRAPI_TOKEN}"} if BRAPI_TOKEN else {}

ATIVOS = ["ITSA4", "BBAS3", "TRPL4", "TAEE11", "BBDC4", "EGIE3", "WEGE3"]

def get_proventos_proximos(ticker):
    url = f"https://brapi.dev/api/quote/{ticker}?modules=dividends"
    try:
        r = requests.get(url, headers=HEADERS)
        data = r.json()
        dividendos = data["results"][0].get("dividendsData", {}).get("dividends", [])
        hoje = datetime.today()
        fim = hoje + timedelta(days=15)
        futuros = []
        for d in dividendos:
            try:
                data_com = datetime.strptime(d.get("dateWith", ""), "%Y-%m-%d")
                data_pag = datetime.strptime(d.get("paymentDate", ""), "%Y-%m-%d")
                if hoje <= data_com <= fim or hoje <= data_pag <= fim:
                    futuros.append({
                        "ticker": ticker,
                        "data_com": data_com.date(),
                        "pagamento": data_pag.date(),
                        "tipo": d.get("label", ""),
                        "valor": d.get("value", 0)
                    })
            except:
                continue
        return futuros
    except Exception as e:
        print(f"[ERRO] {ticker}: {e}")
        return []

@app.route("/")
def index():
    filtro = request.args.get("q", "").upper()
    html = """
    <html><head><meta charset="utf-8"><title>Proventos - Leverage IA</title>
    <style>body{font-family:sans-serif;padding:20px} table{border-collapse:collapse;width:100%} td,th{border:1px solid #ccc;padding:8px;text-align:center} th{background:#f0f0f0}</style>
    </head><body>
    <h1>Proventos nos próximos 15 dias</h1>
    <form>
        <input name="q" placeholder="Filtrar ativo..." value="{filtro}" />
        <button type="submit">Buscar</button>
    </form>
    <table>
    <tr><th>Ativo</th><th>Data Com</th><th>Pagamento</th><th>Tipo</th><th>Valor</th></tr>
    """

    ativos_filtrados = [a for a in ATIVOS if filtro in a] if filtro else ATIVOS
    dados = []
    for ativo in ativos_filtrados:
        dados.extend(get_proventos_proximos(ativo))

    if dados:
        for d in sorted(dados, key=lambda x: x["data_com"]):
            html += f"<tr><td>{d['ticker']}</td><td>{d['data_com']}</td><td>{d['pagamento']}</td><td>{d['tipo']}</td><td>{d['valor']:.2f}</td></tr>"
    else:
        html += "<tr><td colspan='5'>Nenhum dado encontrado nos próximos 15 dias.</td></tr>"

    html += "</table></body></html>"
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
