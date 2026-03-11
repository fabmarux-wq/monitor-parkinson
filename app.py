import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração para não travar no Android
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# Estilo para botões e letras grandes
st.markdown("""
<style>
    .stButton > button { height: 75px !important; font-size: 22px !important; font-weight: bold !important; border-radius: 20px; }
    .stTabs [data-baseweb="tab"] p { font-size: 24px !important; font-weight: bold !important; }
    label { font-size: 22px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_stdio=True)

st.title("📊 Monitor Parkinson Pro")

# Inicializa memória de forma "blindada"
if 'dados' not in st.session_state:
    st.session_state.dados = []
if 'menu' not in st.session_state:
    st.session_state.menu = None

# --- BOTÕES DE ATALHO ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🟢\nMED", use_container_width=True): st.session_state.menu = "Med"
with c2:
    if st.button("🔴\nOFF", use_container_width=True): st.session_state.menu = "OFF"
with c3:
    if st.button("🟡\nEXE", use_container_width=True): st.session_state.menu = "Exe"
with c4:
    if st.button("🔵\nALI", use_container_width=True): st.session_state.menu = "Ali"

st.markdown("---")

# Data de hoje como texto puro para evitar o TypeError
hoje_txt = datetime.now().strftime("%Y-%m-%d")

# --- FORMULÁRIOS ---
if st.session_state.menu:
    st.subheader(f"Registrando {st.session_state.menu}")
    
    # Seletor de tempo com pulo de 10 minutos
    h_escolha = st.time_input("Horário (10 em 10 min):", datetime.now().time(), step=600)
    h_dec = float(h_escolha.hour + h_escolha.minute/60)

    if st.session_state.menu == "Med":
        sel = st.multiselect("Remédios:", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
        if st.button("SALVAR MEDICAÇÃO", use_container_width=True):
            for m in sel:
                n = m.split("(")[1].replace(")", "")
                st.session_state.dados.append({"Data": hoje_txt, "H": h_dec, "Cat": "Med", "Txt": n, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "OFF":
        sints = st.multiselect("Sintomas:", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
        h_fim = st.time_input("Fim do OFF:", h_escolha, step=600)
        if st.button("SALVAR ESTADO OFF", use_container_width=True):
            t = ", ".join(sints) if sints else "OFF"
            st.session_state.dados.append({"Data": hoje_txt, "H": h_dec, "H_Fim": float(h_fim.hour + h_fim.minute/60), "Cat": "OFF", "Txt": t, "Tipo": "Periodo"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Exe":
        txt_e = st.text_input("O que treinou?")
        if st.button("SALVAR TREINO", use_container_width=True):
            st.session_state.dados.append({"Data": hoje_txt, "H": h_dec, "Cat": "Exe", "Txt": txt_e, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Ali":
        txt_a = st.text_input("O que comeu?")
        if st.button("SALVAR COMIDA", use_container_width=True):
            st.session_state.dados.append({"Data": hoje_txt, "H": h_dec, "Cat": "Ali", "Txt": txt_a, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    if st.button("Fechar ❌"):
        st.session_state.menu = None
        st.rerun()

# --- GRÁFICO DIÁRIO TOTALMENTE FIXO ---
if st.session_state.dados:
    df = pd.DataFrame(st.session_state.dados)
    # Filtro de hoje usando texto para ser impossível dar erro de tipo
    df_h = df[df['Data'] == hoje_txt]
    
    if not df_h.empty:
        st.markdown("### Seu Dia:")
        fig = go.Figure()
        cores = {"Med": "#198754", "OFF": "#dc3545", "Exe": "#ffc107", "Ali": "#0dcaf0"}
        for _, r in df_h.iterrows():
            c = cores.get(r['Cat'], "#000")
            if 'H_Fim' in r and not pd.isna(r['H_Fim']):
                fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[float(r['H']), float(r['H_Fim'])], mode='lines', line=dict(color=c, width=40)))
            else:
                fig.add_trace(go.Scatter(x=[r['Cat']], y=[float(r['H'])], mode='markers+text', marker=dict(symbol='square', size=20, color=c), text=[r['Txt']], textposition="middle right"))
        
        # staticPlot trava o gráfico para não sumir nem dar zoom
        fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=600, showlegend=False, dragmode=False)
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

# --- LIMPAR TUDO (SIDEBAR) ---
if st.sidebar.button("🗑️ LIMPAR TESTES"):
    st.session_state.dados = []
    st.rerun()
