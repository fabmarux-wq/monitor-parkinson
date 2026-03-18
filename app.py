import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import requests

# 1. Configuração de tela
st.set_page_config(page_title="Monitor Parkinson Pro", layout="centered")

# --- ⚠️ ÁREA DE CONFIGURAÇÃO (COLE SEUS LINKS AQUI) ⚠️ ---

# Link que você vê na barra do navegador quando abre sua planilha
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1TIzxrVdArj5luQOJW3gob-LcO97l6srZOnI7JUGDPyk/edit"

# O link que o Google te deu no botão "Implantar" (deve terminar em /exec)
URL_POST = "COLE_AQUI_O_LINK_DO_APPS_SCRIPT"

# -------------------------------------------------------

def ler_dados():
    try:
        sheet_id = "1TIzxrVdArj5luQOJW3gob-LcO97l6srZOnI7JUGDPyk"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        df = pd.read_csv(csv_url)
        return df.dropna(subset=['Data', 'Cat'])
    except:
        return pd.DataFrame(columns=["Data", "Cat", "Ini", "Fim", "Desc"])

def enviar_dados(dados):
    # Verifica se o link é válido antes de tentar enviar
    if not URL_POST.startswith("https"):
        st.error("⚠️ ERRO: Você ainda não colou o link do Apps Script na linha 15 do código!")
        return False
    try:
        res = requests.post(URL_POST, json=dados, timeout=10)
        if res.status_code == 200:
            st.success("✅ Registrado com sucesso!")
            return True
        else:
            st.error(f"Erro no Google: {res.status_code}")
            return False
    except:
        st.error("Erro de conexão. Verifique o link do Apps Script.")
        return False

def hora_sp():
    return datetime.now() - timedelta(hours=3)

# Inicialização
if 'off_inicio' not in st.session_state: st.session_state.off_inicio = None
if 'treino_inicio' not in st.session_state: st.session_state.treino_inicio = None
if 'menu' not in st.session_state: st.session_state.menu = None

st.title("📊 Monitor Parkinson Pro")
aba_reg, aba_graf = st.tabs(["📝 REGISTRAR", "📈 HISTÓRICO"])

with aba_reg:
    st.subheader("Controle de Tempo")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔴 INICIAR OFF", use_container_width=True):
            st.session_state.off_inicio = hora_sp().hour + hora_sp().minute/60
            st.rerun()
        if st.button("🏃 INICIAR TREINO", use_container_width=True):
            st.session_state.treino_inicio = hora_sp().hour + hora_sp().minute/60
            st.rerun()
    with c2:
        label_o = "🏁 FINALIZAR OFF" + (" (ATIVO)" if st.session_state.off_inicio else "")
        if st.button(label_o, key="f_off", use_container_width=True):
            if st.session_state.off_inicio:
                agora = hora_sp()
                dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "OFF", "Ini": st.session_state.off_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "OFF"}
                if enviar_dados(dados):
                    st.session_state.off_inicio = None
                    st.rerun()

        label_t = "🏁 FINALIZAR TREINO" + (" (ATIVO)" if st.session_state.treino_inicio else "")
        if st.button(label_t, key="f_tre", use_container_width=True):
            if st.session_state.treino_inicio:
                agora = hora_sp()
                dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "Treino", "Ini": st.session_state.treino_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "Treino"}
                if enviar_dados(dados):
                    st.session_state.treino_inicio = None
                    st.rerun()

    st.divider()
    if st.button("🟢 REGISTRAR REMÉDIOS", use_container_width=True): st.session_state.menu = "Med"
    if st.session_state.menu == "Med":
        remedios = st.multiselect("Remédios:", ["Prolopa BD", "Prolopa HBS", "Prolopa D", "Mantidan", "Pramipexol", "Azilect", "Entacapona"])
        if st.button("💾 CONFIRMAR SALVAMENTO"):
            agora = hora_sp()
            h = agora.hour + agora.minute/60
            dados = {"Data": agora.strftime("%d/%m/%Y"), "Cat": "Medicação", "Ini": h, "Fim": h + 0.5, "Desc": ", ".join(remedios)}
            if enviar_dados(dados):
                st.session_state.menu = None
                st.rerun()

with aba_graf:
    df = ler_dados()
    if not df.empty:
        # Gráfico Diário Travado (Static)
        hoje = hora_sp().strftime("%d/%m/%Y")
        df_h = df[df['Data'] == hoje]
        cores = {"Medicação": "#198754", "OFF": "#dc3545", "Treino": "#ffc107", "Alimentação": "#0dcaf0"}
        
        st.subheader(f"Hoje: {hoje}")
        if not df_h.empty:
            fig = go.Figure()
            for _, r in df_h.iterrows():
                fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['Ini'], r['Fim']], mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=40)))
            fig.update_layout(yaxis=dict(range=[0, 24], dtick=1, title="Horas"), height=450, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
        
        st.divider()
        st.subheader("O Andar da Carruagem (Mês)")
        fig_mes = go.Figure()
        for _, r in df.iterrows():
            fig_mes.add_trace(go.Scatter(x=[r['Data'], r['Data']], y=[r['Ini'], r['Fim']], mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=15)))
        fig_mes.update_layout(yaxis=dict(range=[0, 24], dtick=1), xaxis=dict(type='category'), height=500, showlegend=False)
        st.plotly_chart(fig_mes, use_container_width=True, config={'staticPlot': True})
    else:
        st.info("Aguardando o primeiro registro para mostrar os gráficos...")
