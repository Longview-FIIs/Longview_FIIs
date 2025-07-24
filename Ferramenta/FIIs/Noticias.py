import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup
import os
import re
from io import BytesIO

# --- Funções ---
def buscar_noticias(fii):
    inicio = date.today() - timedelta(days=3)
    hoje = date.today()
    palavra_chave = re.sub(r'\d+', '', fii)
    url = "https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/ListarTitulosNoticias"
    params = {"agencia": 18, "palavra": palavra_chave, "dataInicial": inicio.strftime("%Y-%m-%d"), "dataFinal": hoje.strftime("%Y-%m-%d")}
    res = requests.get(url, params=params)
    if res.status_code == 200:
        noticias = res.json()
        return [{"Fundo": fii, "Data": n.get("NwsMsg", {}).get("dateTime", "sem data"), "Título": n.get("NwsMsg", {}).get("headline", "sem título")} for n in noticias if n.get("NwsMsg")]
    return []

def get_ultimo_dividendo(ticker):
    url = f"https://statusinvest.com.br/fundos-imobiliarios/{ticker.lower()}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    linha = soup.select_one("table tbody tr")
    if linha:
        colunas = linha.find_all("td")
        if len(colunas) >= 4:
            try:
                valor = float(colunas[3].text.strip().replace("R$", "").replace(",", "."))
                return {
                    "Fundo": ticker.upper(),
                    "Data-Base": colunas[1].text.strip(),
                    "Pagamento": colunas[2].text.strip(),
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

# --- Layout ---
st.set_page_config("Analisador FIIs", layout="wide")
st.title("🔍 Analisador de FIIs - Notícias e Dividendos")

# --- Lista FIIs ---
todos_fiis = [     'HGRU11', 'KEVE11', 'BTAL11', 'XPML11', 'JSRE11', 'TVRI11',
    'RECR11', 'KNRI11', 'RBRF11', 'MXRF11', 'RZTR11', 'XPCI11', 'BRCO11', 'HGRE11', 'VGIR11',
    'XPLG11', 'CPTS11', 'ALZR11', 'KFOF11', 'IRDM11', 'RBRR11', 'KNHF11', 'VISC11', 'HGLG11', 'VIUR11',
    'BTLG11', 'MALL11', 'KNHY11', 'MCCI11', 'RBRY11', 'KNSC11', 'PVBI11', 'HSML11', 'KNUQ11', 'KNCR11',
    'LVBI11', 'FATN11', 'GGRC11', 'KORE11', 'TRXF11', 'HGCR11', 'HGFF11', 'VINO11', 'TGAR11', 'KNIP11',
    'RBVA11', 'VILG11', 'VCJR11' ]  # [AQUI MANTÉM A LISTA ORIGINAL COMPLETA COMO ESTÁ]

# --- Estado global ---
def init_session():
    if "favoritos" not in st.session_state:
        st.session_state.favoritos = ["MXRF11", "KNRI11"]
    if "selecionados" not in st.session_state:
        st.session_state.selecionados = st.session_state.favoritos.copy()
    if "filtro" not in st.session_state:
        st.session_state.filtro = ""

init_session()

# --- Filtro ---
filtro = st.text_input("🔎 Filtrar FIIs por nome ou ticker:", value=st.session_state.filtro)
st.session_state.filtro = filtro
fiis_filtrados = [f for f in todos_fiis if filtro.upper() in f.upper()]

# --- Ações ---
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("Selecionar Todos"):
        st.session_state.selecionados = fiis_filtrados.copy()
with col2:
    if st.button("Limpar Seleção"):
        st.session_state.selecionados = []
with col3:
    if st.button("Selecionar Favoritos"):
        st.session_state.selecionados = [f for f in fiis_filtrados if f in st.session_state.favoritos]

# --- Título seção seleção ---
st.markdown("### 🎯 Selecione os FIIs a analisar:")

# --- Análise ---
if st.button("🚀 Analisar Selecionados"):
    with st.spinner("🔄 Coletando dados..."):
        selecionados = st.session_state.selecionados
        todas_noticias = sum([buscar_noticias(fii) for fii in selecionados], [])
        df_noticias = pd.DataFrame(todas_noticias)
        dividendos_atuais = [get_ultimo_dividendo(fii) for fii in selecionados]
        df_atuais = pd.DataFrame(dividendos_atuais)

        historico_path = "historico_dividendos.csv"
        if os.path.exists(historico_path):
            df_anterior = pd.read_csv(historico_path)
        else:
            df_anterior = pd.DataFrame(columns=["Fundo", "Data-Base", "Pagamento", "Último Dividendo (R$)"])

        def comparar(row):
            anterior = df_anterior[df_anterior["Fundo"] == row["Fundo"]]
            if anterior.empty:
                return "NOVO"
            elif row["Data-Base"] != anterior["Data-Base"].values[0]:
                return "NOVA DATA-BASE"
            elif row["Último Dividendo (R$)"] != anterior["Último Dividendo (R$)"].values[0]:
                return "VALOR ALTERADO"
            return "IGUAL"

        df_atuais["Status"] = df_atuais.apply(comparar, axis=1)
        df_atuais.to_csv(historico_path, index=False)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_noticias.to_excel(writer, sheet_name="Notícias", index=False)
            df_atuais.to_excel(writer, sheet_name="Dividendos", index=False)
        buffer.seek(0)

    with st.expander("📰 Notícias Recentes", expanded=True):
        if df_noticias.empty:
            st.info("Nenhuma notícia encontrada.")
        else:
            st.dataframe(df_noticias)

    with st.expander("💰 Comparativo de Dividendos", expanded=True):
        st.dataframe(df_atuais)
        alterados = df_atuais[df_atuais["Status"] == "VALOR ALTERADO"]
        if not alterados.empty:
            st.warning("⚠️ Fundos com alteração no dividendo:")
            for _, row in alterados.iterrows():
                fundo = row["Fundo"]
                atual = row["Último Dividendo (R$)"]
                anterior = df_anterior[df_anterior["Fundo"] == fundo]["Último Dividendo (R$)"].values[0]
                st.markdown(f"🔺 **{fundo}**: R$ {anterior:.2f} ➜ R$ {atual:.2f}")

    st.download_button("⬇️ Baixar Excel com Dados", data=buffer, file_name="FIIs_noticias_dividendos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Armazena estado temporário ---
estado_temporario = {}
for fii in fiis_filtrados:
    col1, col2 = st.columns([0.05, 0.9])
    with col1:
        icone = "⭐" if fii in st.session_state.favoritos else "☆"
        if st.button(icone, key=f"fav_{fii}"):
            if fii in st.session_state.favoritos:
                st.session_state.favoritos.remove(fii)
            else:
                st.session_state.favoritos.append(fii)
            st.rerun()
    with col2:
        estado_temporario[fii] = st.checkbox(
            fii,
            value=fii in st.session_state.selecionados,
            key=f"chk_{fii}"
        )

# Atualiza todos os selecionados de uma vez
st.session_state.selecionados = [fii for fii, marcado in estado_temporario.items() if marcado]

