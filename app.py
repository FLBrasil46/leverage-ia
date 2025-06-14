import os
from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

def extrair_proventos_statusinvest(ticker):
    url = f"https://statusinvest.com.br/acoes/{ticker.lower()}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        tabela = soup.find("table", {"id": "provents-table"})
        linhas = tabela.find_all("tr")[1:]  # pular cabeçalho

        resultados = []
        for tr in linhas:
            colunas = tr.find_all("td")
            if len(colunas) >= 6:
                tipo = colunas[0].text.strip()
                data_com = datetime.strptime(colunas[2].text.strip(), "%d/%m/%Y")
                pagamento = datetime.strptime(colunas[3].text.strip(), "%d/%m/%Y")
                valor = colunas[4].text.strip().replace("R$", "").replace(",", ".")
                resultados.append({
                    "tipo": tipo,
                    "data_com": data_com,
                    "pagamento": pagamento,
                    "valor": float(valor)
                })

        hoje = datetime.now()
        proximos = [r for r in resultados if hoje <= r["data_com"] <= hoje + timedelta(days=15)]
        return proximos

    except Exception as e:
        print(f"Erro ao buscar dados para {ticker}: {e}")
        return []

@app.route("/")
def index():
    ticker = request.args.get("q", "ITSA4").upper()
    dados = extrair_proventos_statusinvest(ticker)

    html = f"""
    <html><head><meta charset="utf-8"><title>Proventos</title></head>
    <body style="font-family: sans-serif; padding: 20px">
        <h1>Proventos nos próximos 15 dias - {ticker}</h1>
        <form method="get">
            <input name="q" value="{ticker}" placeholder="Digite o ticker" style="padding:5px">
            <button type="submit">Buscar</button>
        </form>
        <table border="1" cellpadding="5" style="margin-top: 20px; border-collapse: collapse;">
            <tr><th>Tipo</th><th>Data Com</th><th>Pagamento</th><th>Valor (R$)</th></tr>
    """

    if dados:
        for d in dados:
            html += f"<tr><td>{d['tipo']}</td><td>{d['data_com'].strftime('%d/%m/%Y')}</td><td>{d['pagamento'].strftime('%d/%m/%Y')}</td><td>{d['valor']:.2f}</td></tr>"
    else:
        html += "<tr><td colspan='4'>Sem proventos nos próximos 15 dias.</td></tr>"

    html += "</table></body></html>"
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
