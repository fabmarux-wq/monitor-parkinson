import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# 1. Configuração para o Samsung A56
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# --- AJUSTE DE HORÁRIO (SÃO PAULO - UTC-3) ---
def obter_hora_atual():
    # Ajusta o horário do servidor para o horário de Brasília/SP
    return datetime.now() - timedelta(hours=3)

# --- MEMÓRIA DO APP ---
if 'v16_dados' not in st.session_state: st.session_state['v16_dados'] = []
if 'off_inicio' not in st.session_state: st.session_state['off_inicio'] = None
if 'treino_inicio' not in st.session_state: st.session_state['treino_inicio'] = None
if 'menu' not in st.session_state: st.session_state['menu'] = None

# --- ESTILO DOS BOTÕES ---
cor_off = "#FF0000" if st.session_state.off_inicio else "#F0F2F6"
cor_treino = "#FFD700" if st.session_state.treino_inicio else "#F0F2F6"
txt_off = "white" if st.session_state.off_inicio else "black"

st.markdown(f"""
<style>
    .stButton > button {{ 
        height: 95px !important; font-size: 22px !important; 
        font-weight: bold !important; border-radius: 25px; margin-bottom: 12px;
    }}
    /* Cores dinâmicas para os botões de finalizar */
    button[key="f_off"] {{ background-color: {cor_off} !important; color: {txt_off} !important; border: 3px solid black !important; }}
    button[key="f_tre"] {{ background-color: {cor_treino} !important; color: black !important; border: 3px solid black !important; }}
</style>
""", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson")

# --- ABAS ---
aba_reg, aba_graf = st.tabs(["📝 REGISTRAR", "📈 VER GRÁFICOS"])

with aba_reg:
    st.subheader("Controle de OFF")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔴 INICIAR\nOFF", key="i_off"):
            agora = obter_hora_atual()
            st.session_state.off_inicio = agora.hour + agora.minute/60
            st.rerun()
    with c2:
        # Texto dinâmico com "(ATIVO)"
        label_off = "🏁 FINALIZAR\nOFF (ATIVO)" if st.session_state.off_inicio else "🏁 FINALIZAR\nOFF"
        if st.button(label_off, key="f_off"):
            if st.session_state.off_inicio:
                agora = obter_hora_atual()
                h_fim = agora.hour + agora.minute/60
                st.session_state['v16_dados'].append({
                    "Data": agora.strftime("%d/%m/%Y"),
                    "Cat": "OFF", "Ini": st.session_state.off_inicio, "Fim": h_fim
                })
                st.session_state.off_inicio = None
                st.rerun()

    st.subheader("Controle de Treino")
    c3, c4 = st.columns(2)
    with c3:
        if st.button("🏃 INICIAR\nTREINO", key="i_tre"):
            agora = obter_hora_atual()
            st.session_state.treino_inicio = agora.hour + agora.minute/60
            st.rerun()
    with c4:
        # Texto dinâmico com "(ATIVO)"
        label_tre = "🏁 FINALIZAR\nTREINO (ATIVO)" if st.session_state.treino_inicio else "🏁 FINALIZAR\nTREINO"
        if st.button(label_tre, key="f_tre"):
            if st.session_state.treino_inicio:
                agora = obter_hora_atual()
                h_fim = agora.hour + agora.minute/60
                st.session_state['v16_dados'].append({
                    "Data": agora.strftime("%d/%m/%Y"),
                    "Cat": "Treino", "Ini": st.session_state.treino_inicio, "Fim": h_fim
                })
                st.session_state.treino_inicio = None
                st.rerun()

    st.divider()
    c5, c6 = st.columns(2)
    with c5:
        if st.button("🟢 REMÉDIOS"): st.session_state.menu = "Med"
    with c6:
        if st.button("🔵 COMIDA"): st.session_state.menu = "Ali"

    if st.session_state.menu == "Med":
        remedios = st.multiselect("O que tomou?", ["Prolopa BD", "Mantidan", "Pramipexol", "Rasagilina", "Prolopa HBS", "Prolopa D"])
        if st.button("SALVAR MEDICAMENTO"):
            agora = obter_hora_atual()
            h = agora.hour + agora.minute/60
            st.session_state['v16_dados'].append({
                "Data": agora.strftime("%d/%m/%Y"),
                "Cat": "Medicação", "Ini": h, "Fim": h + 1.0 # Bloco de 1h
            })
            st.session_state.menu = None
            st.rerun()
    elif st.session_state.menu == "Ali":
        comida = st.text_input("O que comeu?")
        if st.button("SALVAR COMIDA"):
            agora = obter_hora_atual()
            h = agora.hour + agora.minute/60
            st.session_state['v16_dados'].append({
                "Data": agora.strftime("%d/%m/%Y"),
                "Cat": "Alimentação", "Ini": h, "Fim": h + 1.0 # Bloco de 1h
            })
            st.session_state.menu = None
            st.rerun()

# --- ABA DE GRÁFICOS ---
with aba_graf:
    if st.session_state['v16_dados']:
        df = pd.DataFrame(st.session_state['v16_dados'])
        hoje = obter_hora_atual().strftime("%d/%m/%Y")
        cores = {"Medicação": "#198754", "OFF": "#dc3545", "Treino": "#ffc107", "Alimentação": "#0dcaf0"}

        # --- GRÁFICO DIÁRIO ---
        st.subheader(f"Hoje: {hoje}")
        df_h = df[df['Data'] == hoje]
        fig_dia = go.Figure()
        for _, r in df_h.iterrows():
            fig_dia.add_trace(go.Scatter(
                x=[r['Cat'], r['Cat']], y=[r['Ini'], r['Fim']],
                mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=50)
            ))
        fig_dia.update_layout(yaxis=dict(range=[0, 24], dtick=1, title="Horas"), 
                             xaxis=dict(title="Atividade"), height=500, showlegend=False)
        st.plotly_chart(fig_dia, use_container_width=True, config={'staticPlot': True})

        st.divider()

        # --- GRÁFICO MENSAL (MAPA) ---
        st.subheader("Mapa Temporal do Mês")
        fig_mes = go.Figure()
        for _, r in df.iterrows():
            fig_mes.add_trace(go.Scatter(
                x=[r['Data'], r['Data']], y=[r['Ini'], r['Fim']],
                mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=20)
            ))
        fig_mes.update_layout(yaxis=dict(range=[0, 24], dtick=1, title="Horas"),
                             xaxis=dict(title="Dias", type='category'), 
                             height=600, showlegend=False)
        st.plotly_chart(fig_mes, use_container_width=True, config={'staticPlot': True})
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Dados", data=csv, file_name='parkinson_diario.csv')
    else:
        st.info("Registre algo para visualizar os gráficos.")

# Reset lateral
if st.sidebar.button("🗑️ LIMPAR TUDO"):
    st.session_state['v16_dados'] = []
    st.session_state.off_inicio = None
    st.session_state.treino_inicio = None
    st.rerun()
