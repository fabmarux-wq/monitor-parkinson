import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# 1. Configuração de tela
st.set_page_config(page_title="Monitor Parkinson Pro", layout="centered")

# --- CONEXÃO SIMPLIFICADA COM GOOGLE SHEETS ---
# Aqui vai o link que você copiou no Passo 1
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1TIzxrVdArj5luQOJW3gob-LcO97l6srZOnI7JUGDPyk/edit?usp=sharing"

def obter_csv_url(url):
    # Transforma o link normal em um link de download direto para o app ler
    return url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')

def carregar_dados_google():
    try:
        # Tenta ler a planilha do Google
        csv_url = obter_csv_url(URL_PLANILHA)
        return pd.read_csv(csv_url)
    except:
        # Se falhar ou estiver vazia, cria uma estrutura básica
        return pd.DataFrame(columns=["Data", "Cat", "Ini", "Fim", "Desc"])

# --- HORÁRIO DE SÃO PAULO ---
def hora_sp():
    return datetime.now() - timedelta(hours=3)

# --- ESTADOS DO APP ---
if 'off_inicio' not in st.session_state: st.session_state.off_inicio = None
if 'treino_inicio' not in st.session_state: st.session_state.treino_inicio = None
if 'menu_aberto' not in st.session_state: st.session_state.menu_aberto = None

# --- ESTILO DOS BOTÕES ---
cor_off = "#FF0000" if st.session_state.off_inicio else "#F0F2F6"
cor_treino = "#FFD700" if st.session_state.treino_inicio else "#F0F2F6"
txt_off = "white" if st.session_state.off_inicio else "black"

st.markdown(f"""
<style>
    .stButton > button {{ height: 95px !important; font-size: 22px !important; font-weight: bold !important; border-radius: 25px; margin-bottom: 12px; }}
    button[key="f_off"] {{ background-color: {cor_off} !important; color: {txt_off} !important; border: 3px solid black !important; }}
    button[key="f_tre"] {{ background-color: {cor_treino} !important; color: black !important; border: 3px solid black !important; }}
</style>
""", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson Pro")

aba_reg, aba_graf = st.tabs(["📝 REGISTRAR", "📈 HISTÓRICO"])

with aba_reg:
    st.subheader("Controle de OFF e Treino")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔴 INICIAR\nOFF", key="i_off"):
            st.session_state.off_inicio = hora_sp().hour + hora_sp().minute/60
            st.rerun()
    with c2:
        label_o = "🏁 FINALIZAR\nOFF (ATIVO)" if st.session_state.off_inicio else "🏁 FINALIZAR\nOFF"
        if st.button(label_o, key="f_off"):
            if st.session_state.off_inicio:
                agora = hora_sp()
                # AVISO: Como não usamos Secrets, para SALVAR você deve baixar o CSV e subir na planilha
                # ou usar o botão de download abaixo.
                st.success(f"OFF Finalizado às {agora.strftime('%H:%M')}! Não esqueça de baixar os dados no fim do dia.")
                st.session_state.off_inicio = None

    # Botões de Medicamentos e Comida (Lista Completa)
    st.divider()
    c5, c6 = st.columns(2)
    with c5:
        if st.button("🟢 REMÉDIOS"): st.session_state.menu_aberto = "Med"
    with c6:
        if st.button("🔵 COMIDA"): st.session_state.menu_aberto = "Ali"

    if st.session_state.menu_aberto == "Med":
        lista = ["Prolopa BD", "Prolopa HBS", "Prolopa D", "Mantidan", "Pramipexol", "Azilect (Rasagilina)", "Entacapona"]
        remedios = st.multiselect("Escolha:", lista)
        if st.button("💾 CONFIRMAR"):
            st.toast(f"Registrado: {remedios}")
            st.session_state.menu_aberto = None

with aba_graf:
    # AQUI O APP LÊ O QUE ESTÁ NA PLANILHA
    df_h = carregar_dados_google()
    if not df_h.empty:
        st.write("### O Andar da Carruagem (Direto do Google)")
        # Gráfico Mensal
        fig_mes = go.Figure()
        for _, r in df_h.iterrows():
            fig_mes.add_trace(go.Scatter(x=[r['Data'], r['Data']], y=[r['Ini'], r['Fim']], mode='lines', line=dict(width=15)))
        fig_mes.update_layout(yaxis=dict(range=[0, 24], dtick=1), xaxis=dict(type='category'), height=500)
        st.plotly_chart(fig_mes, use_container_width=True)
    else:
        st.info("Sua planilha no Google ainda está vazia ou o link está incorreto.")
