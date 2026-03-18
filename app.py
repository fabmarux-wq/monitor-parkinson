import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import requests

# 1. Configuração de tela
st.set_page_config(page_title="Monitor Parkinson Pro", layout="centered")

# --- ⚠️ CONFIGURAÇÃO DOS SEUS LINKS ⚠️ ---
# Link da sua planilha (o que você vê no navegador)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1pDxi9QH70MjAgo3qnt2f2iELJndFzeHg3HeeYH1rtyg/edit?usp=sharing"

# Link do "Porteiro" (O link que o Google deu em 'Implantar')
URL_POST = "https://script.google.com/macros/s/AKfycbxoJVTjuxhwKEjKWgto8agLz2WKSHxLki5kuubatPHSY5ZdhtR37vSDg9oOOjM2aDON9Q/exec"

def ler_dados():
    try:
        # Extrai o ID da planilha e força o download do CSV limpo
        sheet_id = "1TIzxrVdArj5luQOJW3gob-LcO97l6srZOnI7JUGDPyk"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        df = pd.read_csv(csv_url)
        # Garante que os nomes das colunas existam para não dar erro no gráfico
        return df.dropna(subset=['Data', 'Cat'])
    except Exception as e:
        return pd.DataFrame(columns=["Data", "Cat", "Ini", "Fim", "Desc"])

def hora_sp():
    return datetime.now() - timedelta(hours=3)

# Estados do sistema
if 'off_inicio' not in st.session_state: st.session_state.off_inicio = None
if 'treino_inicio' not in st.session_state: st.session_state.treino_inicio = None
if 'menu' not in st.session_state: st.session_state.menu = None

# Estilo para botões grandes e fixos
st.markdown("<style>.stButton > button { height: 90px !important; font-size: 20px !important; font-weight: bold !important; border-radius: 20px; }</style>", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson Pro")
aba_reg, aba_graf = st.tabs(["📝 REGISTRAR", "📈 HISTÓRICO"])

with aba_reg:
    st.subheader("Cronômetros")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔴 INICIAR OFF"):
            st.session_state.off_inicio = hora_sp().hour + hora_sp().minute/60
            st.rerun()
        if st.button("🏃 INICIAR TREINO"):
            st.session_state.treino_inicio = hora_sp().hour + hora_sp().minute/60
            st.rerun()
    with c2:
        if st.button("🏁 FINALIZAR OFF" + (" (ATIVO)" if st.session_state.off_inicio else "")):
            if st.session_state.off_inicio:
                agora = hora_sp()
                dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "OFF", "Ini": st.session_state.off_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "OFF"}
                try:
                    res = requests.post(URL_POST, json=dados, timeout=10)
                    if res.status_code == 200:
                        st.session_state.off_inicio = None
                        st.success("Salvo no Google!")
                        st.rerun()
                except:
                    st.error("Erro ao conectar com o Google. Verifique o link URL_POST.")

        if st.button("🏁 FINALIZAR TREINO" + (" (ATIVO)" if st.session_state.treino_inicio else "")):
            if st.session_state.treino_inicio:
                agora = hora_sp()
                dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "Treino", "Ini": st.session_state.treino_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "Treino"}
                try:
                    requests.post(URL_POST, json=dados, timeout=10)
                    st.session_state.treino_inicio = None
                    st.success("Salvo no Google!")
                    st.rerun()
                except:
                    st.error("Erro ao salvar.")

    st.divider()
    if st.button("🟢 REMÉDIOS", use_container_width=True): st.session_state.menu = "Med"
    if st.session_state.menu == "Med":
        remedios = st.multiselect("O que tomou?", ["Prolopa BD", "Mantidan", "Pramipexol", "Azilect", "Entacapona"])
        if st.button("💾 CONFIRMAR"):
            agora = hora_sp()
            h = agora.hour + agora.minute/60
            dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "Medicação", "Ini": h, "Fim": h + 0.5, "Desc": ", ".join(remedios)}
            requests.post(URL_POST, json=dados)
            st.session_state.menu = None
            st.rerun()

with aba_graf:
    df = ler_dados()
    if not df.empty:
        hoje = hora_sp().strftime("%d/%m/%Y")
        st.subheader(f"Hoje: {hoje}")
        df_h = df[df['Data'] == hoje]
        cores = {"Medicação": "#198754", "OFF": "#dc3545", "Treino": "#ffc107", "Alimentação": "#0dcaf0"}
        
        # GRÁFICO DIÁRIO TRAVADO
        if not df_h.empty:
            fig = go.Figure()
            for _, r in df_h.iterrows():
                fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['Ini'], r['Fim']], mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=45)))
            fig.update_layout(yaxis=dict(range=[0, 24], dtick=1, title="Horas"), height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

        st.divider()
        # GRÁFICO MENSAL TRAVADO (O Andar da Carruagem)
        st.subheader("O Andar da Carruagem (Mês)")
        fig_mes = go.Figure()
        for _, r in df.iterrows():
            fig_mes.add_trace(go.Scatter(x=[r['Data'], r['Data']], y=[r['Ini'], r['Fim']], mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=15)))
        fig_mes.update_layout(yaxis=dict(range=[0, 24], dtick=1), xaxis=dict(type='category'), height=500, showlegend=False)
        st.plotly_chart(fig_mes, use_container_width=True, config={'staticPlot': True})
    else:
        st.info("Aguardando conexão... Se você já salvou dados, verifique o link da planilha.")
