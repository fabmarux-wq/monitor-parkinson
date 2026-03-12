import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# 1. Configuração para o Samsung A56
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# --- CONEXÃO COM A MEMÓRIA (Google Sheets) ---
# Substitua o link abaixo pelo link da sua planilha
url = "https://docs.google.com/spreadsheets/d/1tTwbJHkV9mJIv8BKc1s4wZ5rIZYccoCB584gXVrb-Ao/edit?usp=sharing" 

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        return conn.read(spreadsheet=url)
    except:
        return pd.DataFrame(columns=["Data", "Cat", "Ini", "Fim", "Desc"])

def salvar_no_google(df_novo):
    # Esta função envia os dados para a planilha
    conn.update(spreadsheet=url, data=df_novo)

# --- AJUSTE DE HORA (SÃO PAULO) ---
def obter_hora_atual():
    return datetime.now() - timedelta(hours=3)

# --- INICIALIZAÇÃO ---
df_historico = carregar_dados()

if 'off_inicio' not in st.session_state: st.session_state.off_inicio = None
if 'treino_inicio' not in st.session_state: st.session_state.treino_inicio = None
if 'menu' not in st.session_state: st.session_state.menu = None

# --- ESTILO VISUAL ---
cor_off = "#FF0000" if st.session_state.off_inicio else "#F0F2F6"
cor_treino = "#FFD700" if st.session_state.treino_inicio else "#F0F2F6"

st.markdown(f"""
<style>
    .stButton > button {{ height: 100px !important; font-size: 22px !important; font-weight: bold !important; border-radius: 25px; }}
    button[key="f_off"] {{ background-color: {cor_off} !important; border: 3px solid black !important; }}
    button[key="f_tre"] {{ background-color: {cor_treino} !important; border: 3px solid black !important; }}
</style>
""", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson Pro")

aba_reg, aba_graf = st.tabs(["📝 REGISTRAR", "📈 HISTÓRICO"])

with aba_reg:
    st.subheader("Controle de Tempo")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔴 INICIAR\nOFF", key="i_off"):
            st.session_state.off_inicio = obter_hora_atual().hour + obter_hora_atual().minute/60
            st.rerun()
    with c2:
        txt_o = "🏁 FINALIZAR\nOFF (ATIVO)" if st.session_state.off_inicio else "🏁 FINALIZAR\nOFF"
        if st.button(txt_o, key="f_off"):
            if st.session_state.off_inicio:
                agora = obter_hora_atual()
                novo = pd.DataFrame([{"Data": agora.strftime("%d/%m/%Y"), "Cat": "OFF", "Ini": st.session_state.off_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "OFF"}])
                salvar_no_google(pd.concat([df_historico, novo]))
                st.session_state.off_inicio = None
                st.rerun()

    c3, c4 = st.columns(2)
    with c3:
        if st.button("🏃 INICIAR\nTREINO", key="i_tre"):
            st.session_state.treino_inicio = obter_hora_atual().hour + obter_hora_atual().minute/60
            st.rerun()
    with c4:
        txt_t = "🏁 FINALIZAR\nTREINO (ATIVO)" if st.session_state.treino_inicio else "🏁 FINALIZAR\nTREINO"
        if st.button(txt_t, key="f_tre"):
            if st.session_state.treino_inicio:
                agora = obter_hora_atual()
                novo = pd.DataFrame([{"Data": agora.strftime("%d/%m/%Y"), "Cat": "Treino", "Ini": st.session_state.treino_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "Treino"}])
                salvar_no_google(pd.concat([df_historico, novo]))
                st.session_state.treino_inicio = None
                st.rerun()

with aba_graf:
    if not df_historico.empty:
        hoje = obter_hora_atual().strftime("%d/%m/%Y")
        cores = {"Medicação": "#198754", "OFF": "#dc3545", "Treino": "#ffc107", "Alimentação": "#0dcaf0"}
        
        st.subheader("Gráfico de Hoje")
        df_h = df_historico[df_historico['Data'] == hoje]
        fig_dia = go.Figure()
        for _, r in df_h.iterrows():
            fig_dia.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['Ini'], r['Fim']], mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=50)))
        fig_dia.update_layout(yaxis=dict(range=[0, 24], dtick=1), showlegend=False, height=500)
        st.plotly_chart(fig_dia, use_container_width=True, config={'staticPlot': True})

        st.divider()
        st.subheader("Andar da Carruagem (Mensal)")
        fig_mes = go.Figure()
        for _, r in df_historico.iterrows():
            fig_mes.add_trace(go.Scatter(x=[r['Data'], r['Data']], y=[r['Ini'], r['Fim']], mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=15)))
        fig_mes.update_layout(yaxis=dict(range=[0, 24], dtick=1), xaxis=dict(type='category'), height=500, showlegend=False)
        st.plotly_chart(fig_mes, use_container_width=True, config={'staticPlot': True})
