import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração de tela - Forçando layout fixo
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# Estilo para botões e textos legíveis
st.markdown("""
<style>
    .stButton > button { height: 70px !important; font-size: 20px !important; font-weight: bold !important; border-radius: 15px; }
    .stTabs [data-baseweb="tab"] p { font-size: 22px !important; font-weight: bold !important; }
    label { font-size: 20px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_stdio=True)

st.title("📊 Monitor Parkinson Pro")

if 'dados' not in st.session_state:
    st.session_state.dados = []
if 'menu' not in st.session_state:
    st.session_state.menu = None

# --- BOTÕES DE REGISTRO ---
st.write("### 1. Registrar:")
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

# --- FORMULÁRIOS ---
if st.session_state.menu:
    # SELETOR DE HORA DE 10 EM 10 MINUTOS
    # Nota: step=600 são 600 segundos = 10 minutos
    
    if st.session_state.menu == "Med":
        st.subheader("💊 Registro de Remédios")
        h_m = st.time_input("Horário da Dose (10 em 10 min):", datetime.now().time(), step=600)
        sel = st.multiselect("Remédios (marque vários):", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
        if st.button("SALVAR MEDICAÇÃO", use_container_width=True):
            for m in sel:
                n = m.split("(")[1].replace(")", "")
                st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_m.hour + (h_m.minute/60), "Cat": "Med", "Txt": n, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "OFF":
        st.subheader("⚠️ Registro de OFF")
        sintomas = st.multiselect("Sintomas (marque vários):", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
        col_i, col_f = st.columns(2)
        with col_i: h_ini = st.time_input("Início:", time(8, 0), step=600)
        with col_f: h_fim = st.time_input("Fim:", time(8, 30), step=600)
        
        if st.button("SALVAR ESTADO OFF", use_container_width=True):
            txt = ", ".join(sintomas) if sintomas else "OFF"
            st.session_state.dados.append({
                "Data": str(datetime.now().date()), 
                "H": h_ini.hour + (h_ini.minute/60), 
                "H_Fim": h_fim.hour + (h_fim.minute/60), 
                "Cat": "OFF", "Txt": txt, "Tipo": "Periodo"
            })
            st.session_state.menu = None
            st.rerun()

    if st.button("Cancelar / Fechar"):
        st.session_state.menu = None
        st.rerun()

# --- VISUALIZAÇÃO ---
tab_dia, tab_mes = st.tabs(["📅 Hoje", "📅 Histórico do Mês"])

with tab_dia:
    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)
        df_h = df[df['Data'] == str(datetime.now().date())]
        
        if not df_h.empty:
            fig = go.Figure()
            cores = {"Med": "#198754", "OFF": "#dc3545", "Exe": "#ffc107", "Ali": "#0dcaf0"}
            for _, r in df_h.iterrows():
                c = cores.get(r['Cat'], "#000")
                if 'H_Fim' in r and not pd.isna(r['H_Fim']):
                    fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['H'], r['H_Fim']], mode='lines', line=dict(color=c, width=40)))
                else:
                    fig.add_trace(go.Scatter(x=[r['Cat']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=20, color=c), text=[r['Txt']], textposition="middle right", textfont=dict(size=18)))
            
            # TRAVANDO O GRÁFICO (Configuração Estática)
            fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=600, showlegend=False, dragmode=False)
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})
        else:
            st.write("Sem registros para hoje.")

with tab_mes:
    if st.session_state.dados:
        st.write("Lista de todos os registros:")
        st.dataframe(pd.DataFrame(st.session_state.dados), use_container_width=True)
