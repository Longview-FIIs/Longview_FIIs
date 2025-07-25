import streamlit as st

st.set_page_config("Ferramenta - Menu Principal", layout="centered")
st.markdown("""
<style>
.menu-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 2em;
    gap: 2em;
}
.menu-row {
    display: flex;
    gap: 2em;
}
.menu-btn {
    background: linear-gradient(135deg, #22253b 60%, #393b5b 100%);
    color: #fff;
    font-size: 2em;
    font-weight: 600;
    border: none;
    border-radius: 1.2em;
    padding: 1.2em 2.8em;
    box-shadow: 0 4px 22px #0003;
    transition: transform 0.1s, box-shadow 0.2s, background 0.3s;
    cursor: pointer;
    outline: none;
    min-width: 220px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.7em;
}
.menu-btn:hover {
    background: linear-gradient(135deg, #393b5b 60%, #22253b 100%);
    transform: scale(1.045);
    box-shadow: 0 7px 26px #0004;
}
.menu-btn:active {
    transform: scale(0.97);
}
@media (max-width: 900px) {
    .menu-row { flex-direction: column; gap: 1em; }
    .menu-btn { width: 100%; min-width: 0; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='font-size:2.7em; margin-bottom:0.4em;'>🛠️ Ferramenta - Menu Principal</h1>", unsafe_allow_html=True)
st.write("Escolha um módulo para acessar:")

# JavaScript para navegação (caso queira links externos, use window.location)
st.markdown("""
<div class="menu-container">
  <div class="menu-row">
    <form action="" method="post">
      <button class="menu-btn" name="page" value="fiis" type="submit">📊 FIIs</button>
    </form>
    <form action="" method="post">
      <button class="menu-btn" name="page" value="graficos" type="submit">📈 Gráficos</button>
    </form>
  </div>
  <div class="menu-row">
    <form action="" method="post">
      <button class="menu-btn" name="page" value="modelagem" type="submit">🧮 Modelagem</button>
    </form>
  </div>
</div>
""", unsafe_allow_html=True)

# Navegação sem warnings!
page = st.query_params.get("page")
if page == "fiis":
    st.success("Você clicou em FIIs!")
    # st.switch_page("FIIs/Noticias.py")
elif page == "graficos":
    st.success("Você clicou em Gráficos!")
elif page == "modelagem":
    st.success("Você clicou em Modelagem!")

st.markdown("---")
with st.expander("Sobre"):
    st.write("""
    **Ferramenta de análise**

    - Módulos: FIIs, Gráficos, Modelagem, e outros.
    - Clique nos botões acima para acessar cada função.
    - Desenvolvido por [Seu Nome]
    """)
