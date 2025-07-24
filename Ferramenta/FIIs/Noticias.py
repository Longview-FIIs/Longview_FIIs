import requests
from datetime import date, timedelta

# Lista de FIIs a monitorar
fundos = ['ENDD', 'HGRU', 'KEVE', 'PPEI', 'PFIN', 'VIGT','BTAL', 'XPML', 'JSRE', 'TVRI', 'RECR', 'KNRI', 'RBRF', 'MXRF', 'RZTR', 'XPCI', 'BRCO', 'HGRE', 'HGRU', 'VGIR', 'XPLG', 'CPTS', 'ALZR', 'KFOF', 'IRDM', 'RBRR', 'KNHF', 'VISC', 'HGLG', 'VIUR', 'BTLG', 'MALL', 'KNHY', 'MCCI', 'RBRY', 'KNSC', 'PVBI', 'HSML', 'KNUQ', 'KNCR', 'LVBI', 'FATN', 'GGRC', 'KORE', 'TRXF', 'HGCR', 'HGFF', 'VINO', 'TGAR', 'KNIP', 'RBVA', 'VILG', 'VCJR']

# Datas
inicio = date.today() - timedelta(days=3)
hoje = date.today()
data_inicial = inicio.strftime("%Y-%m-%d")
data_final = hoje.strftime("%Y-%m-%d")

# Loop pelos fundos
for fii in fundos:
    url = "https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/ListarTitulosNoticias"
    params = {
        "agencia": 18,
        "palavra": fii,
        "dataInicial": data_inicial,
        "dataFinal": data_final
    }

    res = requests.get(url, params=params)

    if res.status_code == 200:
        noticias = res.json()
        if noticias:
            print(f"\n🔔 Novidades para {fii}:")
            for n in noticias:
                msg = n.get('NwsMsg', {})
                titulo = msg.get('headline', 'sem título')
                data = msg.get('dateTime', 'sem data')
                id_noticia = msg.get('id')
                print(f"📅 {data}")
                print(f"📌 {titulo}")
    else:
        print(f"❌ Erro para {fii}: Status {res.status_code}")

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_ultimo_dividendo(ticker):
    url = f"https://statusinvest.com.br/fundos-imobiliarios/{ticker.lower()}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    linha = soup.select_one("table tbody tr")
    if linha:
        colunas = linha.find_all("td")
        if len(colunas) >= 4:
            data_base = colunas[1].text.strip()
            pagamento = colunas[2].text.strip()
            valor_raw = colunas[3].text.strip()
            try:
                valor = float(valor_raw.replace("R$", "").replace(",", "."))
                return {
                    "Fundo": ticker.upper(),
                    "Data-Base": data_base,
                    "Pagamento": pagamento,
                    "Último Dividendo (R$)": valor
                }
            except:
                pass
    return {
        "Fundo": ticker.upper(),
        "Data-Base": None,
        "Pagamento": None,
        "Último Dividendo (R$)": None
    }

# Lista de FIIs
fundos = [
    'HGRU11', 'KEVE11', 'BTAL11', 'XPML11', 'JSRE11', 'TVRI11',
    'RECR11', 'KNRI11', 'RBRF11', 'MXRF11', 'RZTR11', 'XPCI11', 'BRCO11', 'HGRE11', 'VGIR11',
    'XPLG11', 'CPTS11', 'ALZR11', 'KFOF11', 'IRDM11', 'RBRR11', 'KNHF11', 'VISC11', 'HGLG11', 'VIUR11',
    'BTLG11', 'MALL11', 'KNHY11', 'MCCI11', 'RBRY11', 'KNSC11', 'PVBI11', 'HSML11', 'KNUQ11', 'KNCR11',
    'LVBI11', 'FATN11', 'GGRC11', 'KORE11', 'TRXF11', 'HGCR11', 'HGFF11', 'VINO11', 'TGAR11', 'KNIP11',
    'RBVA11', 'VILG11', 'VCJR11'
]

# Scraping dos dividendos atuais
dividendos_atuais = [get_ultimo_dividendo(f) for f in fundos]
df_atuais = pd.DataFrame(dividendos_atuais)

# Carregar histórico anterior se existir
csv_path = "historico_dividendos.csv"
if os.path.exists(csv_path):
    df_anterior = pd.read_csv(csv_path)
else:
    df_anterior = pd.DataFrame(columns=["Fundo", "Data-Base", "Pagamento", "Último Dividendo (R$)"])

# Comparação com histórico
def comparar(row):
    fundo = row["Fundo"]
    anterior = df_anterior[df_anterior["Fundo"] == fundo]
    if anterior.empty:
        return "NOVO"
    elif row["Data-Base"] != anterior["Data-Base"].values[0]:
        return "NOVA DATA-BASE"
    elif row["Último Dividendo (R$)"] != anterior["Último Dividendo (R$)"].values[0]:
        return "VALOR ALTERADO"
    else:
        return "IGUAL"

df_atuais["Status"] = df_atuais.apply(comparar, axis=1)

# Salvar novo histórico
df_atuais.to_csv(csv_path, index=False)

# 📢 Printar os fundos que tiveram alteração no valor do dividendo
alterados = df_atuais[df_atuais["Status"] == "VALOR ALTERADO"]
if not alterados.empty:
    print("\n📢 Fundos com ALTERAÇÃO de valor de dividendo:\n")
    for _, row in alterados.iterrows():
        fundo = row["Fundo"]
        atual = row["Último Dividendo (R$)"]
        anterior = df_anterior[df_anterior["Fundo"] == fundo]["Último Dividendo (R$)"].values[0]
        print(f"🔺 {fundo}: {anterior:.2f} ➜ {atual:.2f}")
else:
    print("\n✅ Nenhum fundo teve alteração de valor de dividendo.")
 