import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import requests

# 1. Configuração de tela
st.set_page_config(page_title="Monitor Parkinson Pro", layout="centered")

# --- ⚠️ ATENÇÃO: COLOQUE SEUS LINKS ABAIXO ⚠️ ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/SUA_PLANILHA_AQUI"
URL_POST = "https://script.google.com/macros/s/SEU_SCRIPT_AQUI/exec"

def ler_dados():
    try:
        # Transforma o link da planilha em link de download CSV
        csv_url = URL_PLANILHA.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')
        if "/export" not in csv_url:
             csv_url = URL_PLANILHA.split('/edit')[0] + '/export?format=csv'
        return pd.read_csv(csv_url)
    except Exception as e:
        return pd.DataFrame(columns=["Data", "Cat", "Ini", "Fim", "Desc"])

def hora_sp():
    return datetime.now() - timedelta(hours=3)

# Inicialização de estados
if 'off_inicio' not in st.session_state: st.session_state.off_inicio = None
if 'treino_inicio' not in st.session_state: st.session_state.treino_inicio = None
if 'menu' not in st.session_state: st.session_state.menu = None

# Estilo visual para botões grandes no celular/PC
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
        if st.button("🔴 INICIAR OFF", key="btn_i_off"):
            st.session_state.off_inicio = hora_sp().hour + hora_sp().minute/60
            st.rerun()
        if st.button("🏃 INICIAR TREINO", key="btn_i_tre"):
            st.session_state.treino_inicio = hora_sp().hour + hora_sp().minute/60
            st.rerun()
    with c2:
        label_off = "🏁 FINALIZAR OFF" + (" (ATIVO)" if st.session_state.off_inicio else "")
        if st.button(label_off, key="btn_f_off"):
            if st.session_state.off_inicio:
                agora = hora_sp()
                dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "OFF", "Ini": st.session_state.off_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "OFF"}
                requests.post(URL_POST, json=dados)
                st.session_state.off_inicio = None
                st.success("OFF Salvo!")
                st.rerun()
        
        label_tre = "🏁 FINALIZAR TREINO" + (" (ATIVO)" if st.session_state.treino_inicio else "")
        if st.button(label_tre, key="btn_f_tre"):
            if st.session_state.treino_inicio:
                agora = hora_sp()
                dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "Treino", "Ini": st.session_state.treino_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "Treino"}
                requests.post(URL_POST, json=dados)
                st.session_state.treino_inicio = None
                st.success("Treino Salvo!")
                st.rerun()

    st.divider()
    st.subheader("Registros Rápidos")
    c3, c4 = st.columns(2)
    with c3:
        if st.button("🟢 REMÉDIOS"): st.session_state.menu = "Med"
    with c4:
        if st.button("🔵 COMIDA"): st.session_state.menu = "Ali"

    if st.session_state.menu == "Med":
        remedios = st.multiselect("O que tomou?", ["Prolopa BD", "Prolopa HBS", "Prolopa D", "Mantidan", "Pramipexol", "Azilect", "Entacapona"])
        if st.button("💾 CONFIRMAR MEDICAMENTO"):
            agora = hora_sp()
            h = agora.hour + agora.minute/60
            dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "Medicação", "Ini": h, "Fim": h + 0.5, "Desc": ", ".join(remedios)}
            requests.post(URL_POST, json=dados)
            st.session_state.menu = None
            st.success("Remédios salvos!")
            st.rerun()
            
    elif st.session_state.menu == "Ali":
        comida = st.text_input("O que comeu?")
        if st.button("💾 CONFIRMAR COMIDA"):
            agora = hora_sp()
            h = agora.hour + agora.minute/60
            dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "Alimentação", "Ini": h, "Fim": h + 0.5, "Desc": comida}
            requests.post(URL_POST, json=dados)
            st.session_state.menu = None
            st.success("Comida salva!")
            st.rerun()

with aba_graf:
    df = ler_dados()
    if not df.empty:
        hoje = hora_sp().strftime("%d/%m/%Y")
        st.subheader(f"Hoje: {hoje}")
        
        # Filtra dados de hoje
        df_h = df[df['Data'] == hoje]
        
        fig = go.Figure()
        cores = {"Medicação": "#198754", "OFF": "#dc3545", "Treino": "#ffc107", "Alimentação": "#0dcaf0"}
        
        for _, r in df_h.iterrows():
            fig.add_trace(go.Scatter(
                x=[r['Cat'], r['Cat']], 
                y=[r['Ini'], r['Fim']], 
                mode='lines', 
                line=dict(color=cores.get(r['Cat'], "#000"), width=40),
                name=str(r['Cat'])
            ))
        
        fig.update_layout(
            yaxis=dict(range=[0, 24], dtick=1, title="Horas do Dia"),
            xaxis=dict(title="Categorias"),
            height=500, showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

        st.divider()
        st.subheader("O Andar da Carruagem (Mês)")
        fig_mes = go.Figure()
        for _, r in df.iterrows():
            fig_mes.add_trace(go.Scatter(
                x=[r['Data'], r['Data']], 
                y=[r['Ini'], r['Fim']], 
                mode='lines', 
                line=dict(color=cores.get(r['Cat'], "#000"), width=15)
            ))
        fig_mes.update_layout(
            yaxis=dict(range=[0, 24], dtick=1, title="Horas"),
            xaxis=dict(type='category', title="Dias"), 
            height=500, showlegend=False
        )
        st.plotly_chart(fig_mes, use_container_width=True, config={'staticPlot': True})
    else:
        st.info("Nada registrado na planilha ainda. O 'Andar da Carruagem' aparecerá assim que você salvar o primeiro dado.")
