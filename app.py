import os
import requests
from flask import Flask
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = Flask(__name__)

URL = "https://statusinvest.com.br/acoes/proventos"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_proventos_filtrados():
    try:
        response = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table")
        if not table:
            return []

        hoje = datetime.today()
        trinta_dias_atras = hoje - timedelta(days=30)

        proventos = []
        for row in table.tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 6:
                ativo = cols[0].text.strip()
                tipo = cols[1].text.strip()
                data_com = parse_data(cols[2].text.strip())
                valor = float(cols[3].text.strip().replace("R$", "").replace(",", "."))
                pagamento = parse_data(cols[4].text.strip())

                # Filtra por datas dentro dos últimos 30 dias ou futuras
                if (data_com and data_com >= trinta_dias_atras) or (pagamento and pagamento >= trinta_dias_atras):
                    proventos.append({
                        "ativo": ativo,
                        "tipo": tipo,
                        "data_com": data_com.strftime("%d/%m/%Y") if data_com else "",
                        "pagamento": pagamento.strftime("%d/%m/%Y") if pagamento else "",
                        "valor": valor
                    })
        return proventos
    except Exception as e:
        print("Erro:", e)
        return []

def parse_data(data_str):
    try:
        return datetime.strptime(data_str.strip(), "%d/%m/%Y")
    except:
        return None

@app.route("/")
def index():
    proventos = get_proventos_filtrados()
    rows = ""
    for p in proventos:
        rows += f"<tr><td>{p['ativo']}</td><td>{p['tipo']}</td><td>{p['data_com']}</td><td>{p['pagamento']}</td><td>R$ {p['valor']:.2f}</td></tr>"

    labels = [f"'{p['ativo']}'" for p in proventos]
    values = [p["valor"] for p in proventos]

    html = f"""
    <html><head><meta charset="utf-8"><title>Proventos Recentes</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script></head>
    <body class="p-4">
        <div class="container">
            <h1 class="mb-4">Proventos (últimos 30 dias ou futuros)</h1>
            <table class="table table-striped table-bordered">
                <thead class="table-dark"><tr>
                    <th>Ativo</th><th>Tipo</th><th>Data COM</th><th>Pagamento</th><th>Valor</th>
                </tr></thead>
                <tbody>{rows if rows else '<tr><td colspan="5">Nenhum dado encontrado</td></tr>'}</tbody>
            </table>

            <h4 class="mt-5">Gráfico de Valores</h4>
            <canvas id="grafico" height="100"></canvas>
        </div>
        <script>
        new Chart(document.getElementById("grafico"), {{
            type: 'bar',
            data: {{
                labels: [{",".join(labels)}],
                datasets: [{{
                    label: 'Valor (R$)',
                    data: {values},
                    backgroundColor: 'rgba(54, 162, 235, 0.5)'
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
