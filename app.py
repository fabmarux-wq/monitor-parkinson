import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Configuração para celular
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# Estilo para botões grandes e fáceis de clicar
st.markdown("""
<style>
    .stButton > button { height: 60px !important; font-size: 20px !important; font-weight: bold !important; border-radius: 15px; }
    .css-1offfwp e1tz724v1 { font-size: 25px !important; }
    h3 { font-size: 22px !important; }
</style>
""", unsafe_allow_stdio=True)

st.title("📊 Monitor Parkinson Pro")

# Inicializa a memória
if 'dados' not in st.session_state:
    st.session_state.dados = []
if 'menu' not in st.session_state:
    st.session_state.menu = None
# Inicializa horários manuais se não existirem
if 'h_manual' not in st.session_state:
    st.session_state.h_manual = datetime.now().hour
if 'm_manual' not in st.session_state:
    st.session_state.m_manual = (datetime.now().minute // 10) * 10

# --- BOTÕES DE CATEGORIA ---
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

# --- AJUSTE DE HORÁRIO MANUAL (MAIS E MENOS) ---
if st.session_state.menu:
    st.subheader(f"Registrando {st.session_state.menu}")
    
    st.write("**Ajuste o Horário (10 em 10 min):**")
    col_h1, col_h2, col_m1, col_m2 = st.columns([1,1,1,1])
    
    with col_h1:
        if st.button("H -"): st.session_state.h_manual = (st.session_state.h_manual - 1) % 24
    with col_h2:
        if st.button("H +"): st.session_state.h_manual = (st.session_state.h_manual + 1) % 24
    with col_m1:
        if st.button("M -"): st.session_state.m_manual = (st.session_state.m_manual - 10) % 60
    with col_m2:
        if st.button("M +"): st.session_state.m_manual = (st.session_state.m_manual + 10) % 60
    
    # Exibe o horário selecionado bem grande
    st.info(f"Horário Selecionado: **{st.session_state.h_manual:02d}:{st.session_state.m_manual:02d}**")
    h_dec = float(st.session_state.h_manual + st.session_state.m_manual/60)
    hoje = datetime.now().strftime("%d/%m/%Y")

    # --- CAMPOS ESPECÍFICOS ---
    if st.session_state.menu == "Med":
        remedios = st.multiselect("Remédios:", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
        if st.button("SALVAR AGORA", use_container_width=True):
            for r in remedios:
                n = r.split("(")[1].replace(")", "")
                st.session_state.dados.append({"Data": hoje, "H": h_dec, "Cat": "Med", "Txt": n})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "OFF":
        sints = st.multiselect("Sintomas:", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
        if st.button("SALVAR INÍCIO DO OFF", use_container_width=True):
            txt = ", ".join(sints) if sints else "OFF"
            st.session_state.dados.append({"Data": hoje, "H": h_dec, "Cat": "OFF", "Txt": txt})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Exe":
        atv = st.text_input("Atividade:")
        if st.button("SALVAR TREINO", use_container_width=True):
            st.session_state.dados.append({"Data": hoje, "H": h_dec, "Cat": "Exe", "Txt": atv})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Ali":
        com = st.text_input("O que comeu?")
        if st.button("SALVAR COMIDA", use_container_width=True):
            st.session_state.dados.append({"Data": hoje, "H": h_dec, "Cat": "Ali", "Txt": com})
            st.session_state.menu = None
            st.rerun()

    if st.button("Cancelar"):
        st.session_state.menu = None
        st.rerun()

# --- GRÁFICO FIXO ---
if st.session_state.dados:
    st.divider()
    df = pd.DataFrame(st.session_state.dados)
    fig = go.Figure()
    cores = {"Med": "#198754", "OFF": "#dc3545", "Exe": "#ffc107", "Ali": "#0dcaf0"}
    
    for _, r in df.iterrows():
        c = cores.get(r['Cat'], "#000")
        fig.add_trace(go.Scatter(x=[r['Cat']], y=[float(r['H'])], mode='markers+text', 
                                 marker=dict(symbol='square', size=20, color=c), 
                                 text=[r['Txt']], textposition="middle right"))
    
    fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=600, showlegend=False, dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

# Botão de reset
if st.sidebar.button("🗑️ Limpar Tudo"):
    st.session_state.dados = []
    st.rerun()
