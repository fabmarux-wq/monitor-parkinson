import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# 1. Configuração para o Samsung A56
st.set_page_config(page_title="Monitor Parkinson Pro", layout="centered")

# --- CONEXÃO OFICIAL COM MEMÓRIA PERMANENTE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados():
    try:
        # Lê os dados da planilha configurada nos Secrets
        return conn.read(ttl=0) 
    except:
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
    st.subheader("Controle de Tempo")
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
                df_atual = ler_dados()
                novo = pd.DataFrame([{"Data": agora.strftime("%d/%m/%Y"), "Cat": "OFF", "Ini": st.session_state.off_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "OFF"}])
                # SALVA NO GOOGLE SHEETS
                conn.update(data=pd.concat([df_atual, novo], ignore_index=True))
                st.session_state.off_inicio = None
                st.success("Salvo no Google!")
                st.rerun()

    # Treino (Mesma Lógica)
    c3, c4 = st.columns(2)
    with c3:
        if st.button("🏃 INICIAR\nTREINO", key="i_tre"):
            st.session_state.treino_inicio = hora_sp().hour + hora_sp().minute/60
            st.rerun()
    with c4:
        label_t = "🏁 FINALIZAR\nTREINO (ATIVO)" if st.session_state.treino_inicio else "🏁 FINALIZAR\nTREINO"
        if st.button(label_t, key="f_tre"):
            if st.session_state.treino_inicio:
                agora = hora_sp()
                df_atual = ler_dados()
                novo = pd.DataFrame([{"Data": agora.strftime("%d/%m/%Y"), "Cat": "Treino", "Ini": st.session_state.treino_inicio, "Fim": agora.hour + agora.minute/60, "Desc": "Treino"}])
                conn.update(data=pd.concat([df_atual, novo], ignore_index=True))
                st.session_state.treino_inicio = None
                st.success("Salvo no Google!")
                st.rerun()

    st.divider()
    c5, c6 = st.columns(2)
    with c5:
        if st.button("🟢 REMÉDIOS"): st.session_state.menu_aberto = "Med"
    with c6:
        if st.button("🔵 COMIDA"): st.session_state.menu_aberto = "Ali"

    if st.session_state.menu_aberto == "Med":
        remedios = st.multiselect("O que tomou?", ["Prolopa BD", "Prolopa HBS", "Prolopa D", "Mantidan", "Pramipexol", "Azilect (Rasagilina)", "Entacapona"])
        if st.button("💾 CONFIRMAR"):
            agora = hora_sp()
            df_atual = ler_dados()
            h = agora.hour + agora.minute/60
            novo = pd.DataFrame([{"Data": agora.strftime("%d/%m/%Y"), "Cat": "Medicação", "Ini": h, "Fim": h + 0.5, "Desc": ", ".join(remedios)}])
            conn.update(data=pd.concat([df_atual, novo], ignore_index=True))
            st.session_state.menu_aberto = None
            st.rerun()

with aba_graf:
    df_h = ler_dados()
    if not df_h.empty:
        # Gráfico diário e mensal como você pediu: 0-24h
        hoje = hora_sp().strftime("%d/%m/%Y")
        cores = {"Medicação": "#198754", "OFF": "#dc3545", "Treino": "#ffc107", "Alimentação": "#0dcaf0"}
        
        st.subheader(f"Hoje: {hoje}")
        df_hoje = df_h[df_h['Data'] == hoje]
        fig_dia = go.Figure()
        for _, r in df_hoje.iterrows():
            fig_dia.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['Ini'], r['Fim']], mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=50)))
        fig_dia.update_layout(yaxis=dict(range=[0, 24], dtick=1, title="Horas"), height=550, showlegend=False)
        st.plotly_chart(fig_dia, use_container_width=True, config={'staticPlot': True})

        st.divider()
        st.subheader("O Andar da Carruagem (Mês)")
        fig_mes = go.Figure()
        for _, r in df_h.iterrows():
            fig_mes.add_trace(go.Scatter(x=[r['Data'], r['Data']], y=[r['Ini'], r['Fim']], mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=15)))
        fig_mes.update_layout(yaxis=dict(range=[0, 24], dtick=1), xaxis=dict(type='category'), height=550, showlegend=False)
        st.plotly_chart(fig_mes, use_container_width=True, config={'staticPlot': True})
    else:
        st.info("Sua planilha está vazia. Comece a registrar para ver o histórico.")
