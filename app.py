import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Configuração para o Samsung A56
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# --- ESTADO DO APLICATIVO ---
if 'v10_dados' not in st.session_state: st.session_state['v10_dados'] = []
if 'off_inicio' not in st.session_state: st.session_state['off_inicio'] = None
if 'treino_inicio' not in st.session_state: st.session_state['treino_inicio'] = None
if 'menu' not in st.session_state: st.session_state['menu'] = None

# --- ESTILO DOS BOTÕES (Cores Dinâmicas) ---
st.markdown("""
<style>
    .stButton > button { 
        height: 90px !important; font-size: 22px !important; 
        font-weight: bold !important; border-radius: 25px;
        margin-bottom: 10px; width: 100%;
    }
    /* Cores quando ativos */
    .btn-off-ativo button { background-color: #ff4b4b !important; color: white !important; border: 3px solid black !important; }
    .btn-treino-ativo button { background-color: #ffeb3b !important; color: black !important; border: 3px solid black !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson Pro")

# Função para salvar eventos no banco de dados
def salvar_evento(cat, desc, h_ini, h_fim=None):
    agora = datetime.now()
    st.session_state['v10_dados'].append({
        "Data": agora.strftime("%d/%m/%Y"),
        "Categoria": cat,
        "Descricao": desc,
        "Inicio": float(h_ini),
        "Fim": float(h_fim) if h_fim is not None else None
    })

# --- BLOCO 1: ESTADO OFF ---
st.subheader("🔴 Controle de OFF")
c1, c2 = st.columns(2)
with c1:
    if st.button("INICIAR\nOFF", key="off_start"):
        agora = datetime.now()
        st.session_state.off_inicio = agora.hour + agora.minute/60
        st.rerun()
with c2:
    if st.session_state.off_inicio is not None:
        st.markdown('<div class="btn-off-ativo">', unsafe_allow_html=True)
        if st.button("FINALIZAR\nOFF (ATIVO)", key="off_end"):
            agora = datetime.now()
            salvar_evento("OFF", "Duração OFF", st.session_state.off_inicio, agora.hour + agora.minute/60)
            st.session_state.off_inicio = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.button("FINALIZAR\nOFF", disabled=True)

# --- BLOCO 2: TREINO ---
st.subheader("🏃 Controle de Treino")
c3, c4 = st.columns(2)
with c3:
    if st.button("INICIAR\nTREINO", key="treino_start"):
        agora = datetime.now()
        st.session_state.treino_inicio = agora.hour + agora.minute/60
        st.rerun()
with c4:
    if st.session_state.treino_inicio is not None:
        st.markdown('<div class="btn-treino-ativo">', unsafe_allow_html=True)
        if st.button("FINALIZAR\nTREINO (ATIVO)", key="treino_end"):
            agora = datetime.now()
            salvar_evento("Treino", "Duração Treino", st.session_state.treino_inicio, agora.hour + agora.minute/60)
            st.session_state.treino_inicio = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.button("FINALIZAR\nTREINO", disabled=True)

st.divider()

# --- BLOCO 3: REGISTROS PONTUAIS ---
c5, c6 = st.columns(2)
with c5:
    if st.button("🟢 REMÉDIOS"): st.session_state.menu = "Med"
with c6:
    if st.button("🔵 COMIDA"): st.session_state.menu = "Ali"

# Formulários Rápidos
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

if st.session_state.menu and st.button("Fechar X"):
    st.session_state.menu = None
    st.rerun()

# --- GR
