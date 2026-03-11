import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# 1. Configuração para o Samsung A56
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# --- MEMÓRIA DO APLICATIVO ---
if 'v13_dados' not in st.session_state: st.session_state['v13_dados'] = []
if 'off_inicio' not in st.session_state: st.session_state['off_inicio'] = None
if 'treino_inicio' not in st.session_state: st.session_state['treino_inicio'] = None
if 'menu' not in st.session_state: st.session_state['menu'] = None

# --- ESTILO DOS BOTÕES (CORRIGIDO) ---
# Usamos cores vibrantes para você identificar o estado ativo
cor_off = "#FF0000" if st.session_state.off_inicio else "#f0f2f6"
cor_treino = "#FFD700" if st.session_state.treino_inicio else "#f0f2f6"
texto_off = "white" if st.session_state.off_inicio else "black"
texto_treino = "black"

st.markdown(f"""
<style>
    .stButton > button {{ 
        height: 95px !important; font-size: 22px !important; 
        font-weight: bold !important; border-radius: 25px;
        margin-bottom: 10px; width: 100%;
    }}
    /* Estilo para o botão Finalizar OFF */
    div[data-testid="column"]:nth-of-type(2) > div > div > div > div:nth-of-type(1) button {{
        background-color: {cor_off} !important;
        color: {texto_off} !important;
    }}
    /* Estilo para o botão Finalizar Treino */
    div[data-testid="column"]:nth-of-type(2) > div > div > div > div:nth-of-type(2) button {{
        background-color: {cor_treino} !important;
        color: {texto_treino} !important;
    }}
</style>
""", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson Pro")

# Função para salvar eventos
def salvar_evento(cat, desc, h_ini, h_fim=None):
    agora = datetime.now()
    # Se for medicação ou alimentação, damos 1 hora de duração para aparecer no gráfico
    if cat in ["Medicação", "Alimentação"] and h_fim is None:
        h_fim = h_ini + 1.0
    
    st.session_state['v13_dados'].append({
        "Data": agora.strftime("%d/%m/%Y"),
        "Categoria": cat,
        "Descricao": desc,
        "Inicio": float(h_ini),
        "Fim": float(h_fim) if h_fim is not None else h_ini + 0.1,
        "Qtd": 1
    })

# --- CONTROLES DE INÍCIO E FIM ---
st.subheader("🔴 Controle de OFF")
c1, c2 = st.columns(2)
with c1:
    if st.button("INICIAR\nOFF", key="off_start"):
        st.session_state.off_inicio = datetime.now().hour + datetime.now().minute/60
        st.rerun()
with c2:
    if st.button("FINALIZAR\nOFF", key="off_end"):
        if st.session_state.off_inicio:
            salvar_evento("OFF", "Duração OFF", st.session_state.off_inicio, datetime.now().hour + datetime.now().minute/60)
            st.session_state.off_inicio = None
            st.rerun()

st.subheader("🏃 Controle de Treino")
c3, c4 = st.columns(2)
with c3:
    if st.button("INICIAR\nTREINO", key="treino_start"):
        st.session_state.treino_inicio = datetime.now().hour + datetime.now().minute/60
        st.rerun()
with c4:
    if st.button("FINALIZAR\nTREINO", key="treino_end"):
        if st.session_state.treino_inicio:
            salvar_evento("Treino", "Duração Treino", st.session_state.treino_inicio, datetime.now().hour + datetime.now().minute/60)
            st.session_state.treino_inicio = None
            st.rerun()

st.divider()

# --- REGISTROS PONTUAIS ---
c5, c6 = st.columns(2)
with c5:
    if st.button("🟢 REMÉDIOS"): st.session_state.menu = "Med"
with c6:
    if st.button("🔵 COMIDA"): st.session_state.menu = "Ali"

if st.session_state.menu == "Med":
    remedios = st.multiselect("O que tomou?", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
    if st.button("SALVAR AGORA"):
        agora = datetime.now()
        salvar_evento("Medicação", ", ".join(remedios), agora.hour + agora.minute/60)
        st.session_state.menu = None
        st.rerun()
elif st.session_state.menu == "Ali":
    comida = st.text_input("O que comeu?")
    if st.button("SALVAR COMIDA"):
        agora = datetime.now()
        salvar_evento("Alimentação", comida, agora.hour + agora.minute/60)
        st.session_state.menu = None
        st.rerun()

# ---
