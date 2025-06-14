import os
import requests
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

def buscar_dividendos(ticker):
    token = os.getenv("BRAPI_TOKEN")
    url = f"https://brapi.dev/api/stock/dividends/{ticker}?token={token}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get("dividends", [])
    except:
        pass
    return []

@app.route("/")
def index():
    ativo = request.args.get("ativo", "").upper()
    dividendos = []
    if ativo:
        dividendos = buscar_dividendos(ativo)
    return render_template("index.html", ativo=ativo, dividendos=dividendos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)