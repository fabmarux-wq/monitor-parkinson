import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import requests

# 1. Configuração de tela
st.set_page_config(page_title="Monitor Parkinson Pro", layout="centered")

# --- ⚠️ CONFIGURAÇÃO DOS SEUS LINKS ⚠️ ---
# Link da sua planilha (Já corrigido com aspas)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1TIzxrVdArj5luQOJW3gob-LcO97l6srZOnI7JUGDPyk/edit?usp=sharing"

# Link do Porteiro (COLE O SEU LINK DO APPS SCRIPT ABAIXO ENTRE AS ASPAS)
URL_POST = "COLE_AQUI_O_LINK_DO_APPS_SCRIPT"

def ler_dados():
    try:
        # Extrai o ID da planilha para gerar o link de exportação CSV
        sheet_id = "1TIzxrVdArj5luQOJW3gob-LcO97l6srZOnI7JUGDPyk"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(csv_url)
        return df.dropna(how='all')
    except Exception as e:
        return pd.DataFrame(columns=["Data", "Cat", "Ini", "Fim", "Desc"])

def hora_sp():
    return datetime.now() - timedelta(hours=3)

# Inicialização de estados do aplicativo
if 'off_inicio' not in st.session_state: st.session_state.off_inicio = None
if 'treino_inicio' not in st.session_state: st.session_state.treino_inicio = None
if 'menu' not in st.session_state: st.session_state.menu = None

# Estilo para botões grandes e fáceis de clicar
st.markdown("""
<style>
    .stButton > button { height: 90px !important; font-size: 20px !important; font-weight: bold !important; border-radius: 20px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson Pro")
aba_reg, aba_graf = st.tabs(["📝 REGISTRAR", "📈 HISTÓRICO"])

with aba_reg:
    st.subheader("⏱️ Cronômetros")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔴 INICIAR OFF"):
            st.session_state.off_inicio = hora_sp().hour + hora_sp().minute/60
            st.rerun()
        if st.button("🏃 INICIAR TREINO"):
            st.session_state.treino_inicio = hora_sp().hour + hora_sp().minute/60
            st.rerun()
    with c2:
        txt_off = "🏁 FINALIZAR OFF" + (" (ATIVO)" if st.session_state.off_inicio else "")
        if st.button(txt_off, key="f_off"):
            if st.session_state.off_inicio:
                agora = hora_sp()
                dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "OFF", "Ini": st.session_state.off_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "OFF"}
                requests.post(URL_POST, json=dados)
                st.session_state.off_inicio = None
                st.success("OFF Salvo com sucesso!")
                st.rerun()
        
        txt_tre = "🏁 FINALIZAR TREINO" + (" (ATIVO)" if st.session_state.treino_inicio else "")
        if st.button(txt_tre, key="f_tre"):
            if st.session_state.treino_inicio:
                agora = hora_sp()
                dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "Treino", "Ini": st.session_state.treino_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "Treino"}
                requests.post(URL_POST, json=dados)
                st.session_state.treino_inicio = None
                st.success("Treino Salvo com sucesso!")
                st.rerun()

    st.divider()
    if st.button("🟢 REGISTRAR REMÉDIOS", use_container_width=True): st.session_state.menu = "Med"
    if st.button("🔵 REGISTRAR COMIDA", use_container_width=True): st.session_state.menu = "Ali"

    if st.session_state.menu == "Med":
        remedios = st.multiselect("O que tomou?", ["Prolopa BD", "Mantidan", "Pramipexol", "Azilect", "Entacapona"])
        if st.button("💾 CONFIRMAR MEDICAMENTOS"):
            agora = hora_sp()
            h = agora.hour + agora.minute/60
            dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "Medicação", "Ini": h, "Fim": h + 0.5, "Desc": ", ".join(remedios)}
            requests.post(URL_POST, json=dados)
            st.session_state.menu = None
            st.success("Medicamentos registrados!")
            st.rerun()
            
    elif st.session_state.menu == "Ali":
        comida = st.text_input("O que comeu?")
        if st.button("💾 CONFIRMAR COMIDA"):
            agora = hora_sp()
            h = agora.hour + agora.minute/60
            dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "Alimentação", "Ini": h, "Fim": h + 0.5, "Desc": comida}
            requests.post(URL_POST, json=dados)
            st.session_state.menu = None
            st.success("Alimentação registrada!")
            st.rerun()

with aba_graf:
    df = ler_dados()
    if not df.empty:
        hoje = hora_sp().strftime("%d/%m/%Y")
        st.subheader(f"Hoje: {hoje}")
        df_h = df[df['Data'] == hoje]
        cores = {"Medicação": "#198754", "OFF": "#dc3545", "Treino": "#ffc107", "Alimentação": "#0dcaf0"}
        
        if not df_h.empty:
            fig = go.Figure()
            for _, r in df_h.iterrows():
                fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['Ini'], r['Fim']], mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=40)))
            fig.update_layout(yaxis=dict(range=[0, 24], dtick=1, title="Horas"), height=450, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("O Andar da Carruagem (Mês)")
        fig_mes = go.Figure()
        for _, r in df.iterrows():
            fig_mes.add_trace(go.Scatter(x=[r['Data'], r['Data']], y=[r['Ini'], r['Fim']], mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=15)))
        fig_mes.update_layout(yaxis=dict(range=[0, 24], dtick=1), xaxis=dict(type='category'), height=500, showlegend=False)
        st.plotly_chart(fig_mes, use_container_width=True)
    else:
        st.info("Nenhum dado encontrado. Faça o seu primeiro registro para ver os gráficos.")
