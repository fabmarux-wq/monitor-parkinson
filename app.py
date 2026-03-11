import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração para evitar erros no Android
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

st.markdown("### 📊 Monitor Parkinson Pro")

# --- MEMÓRIA SEGURA ---
if 'dados' not in st.session_state:
    st.session_state.dados = []
if 'menu' not in st.session_state:
    st.session_state.menu = None

# --- BOTÕES DE ATALHO (LARGURA TOTAL) ---
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

hoje_hoje = datetime.now().strftime("%Y-%m-%d")

# --- FORMULÁRIOS COMPLETOS ---
if st.session_state.menu:
    st.info(f"Registrando: {st.session_state.menu}")
    
    # Horário com pulo de 10 minutos (600 segundos)
    h_escolha = st.time_input("Horário (10 em 10 min):", datetime.now().time(), step=600)
    h_dec = float(h_escolha.hour + h_escolha.minute/60)

    if st.session_state.menu == "Med":
        sel = st.multiselect("Remédios:", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
        if st.button("SALVAR MEDICAÇÃO", use_container_width=True):
            for m in sel:
                n = m.split("(")[1].replace(")", "")
                st.session_state.dados.append({"Data": hoje_hoje, "H": h_dec, "Cat": "Med", "Txt": n, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "OFF":
        sints = st.multiselect("Sintomas:", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
        h_fim_escolha = st.time_input("Término do OFF:", datetime.now().time(), step=600)
        if st.button("SALVAR ESTADO OFF", use_container_width=True):
            t = ", ".join(sints) if sints else "OFF"
            st.session_state.dados.append({
                "Data": hoje_hoje, "H": h_dec, 
                "H_Fim": float(h_fim_escolha.hour + h_fim_escolha.minute/60), 
                "Cat": "OFF", "Txt": t, "Tipo": "Periodo"
            })
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Exe":
        tipo_exe = st.text_input("O que treinou? (ex: Caminhada, Fisioterapia)")
        if st.button("SALVAR EXERCÍCIO", use_container_width=True):
            st.session_state.dados.append({"Data": hoje_hoje, "H": h_dec, "Cat": "Exe", "Txt": tipo_exe, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Ali":
        comida = st.text_input("O que comeu?")
        if st.button("SALVAR ALIMENTAÇÃO", use_container_width=True):
            st.session_state.dados.append({"Data": hoje_hoje, "H": h_dec, "Cat": "Ali", "Txt": comida, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    if st.button("Fechar ❌"):
        st.session_state.menu = None
        st.rerun()

# --- GRÁFICO DIÁRIO FIXO ---
if st.session_state.dados:
    df = pd.DataFrame(st.session_state.dados)
    df_h = df[df['Data'] == hoje_hoje]
    
    if not df_h.empty:
        st.markdown("### Seu Dia Hoje:")
        fig = go.Figure()
        cores = {"Med": "#198754", "OFF": "#dc3545", "Exe": "#ffc107", "Ali": "#0dcaf0"}
        for _, r in df_h.iterrows():
            c = cores.get(r['Cat'], "#000")
            if 'H_Fim' in r and not pd.isna(r['H_Fim']):
                fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[float(r['H']), float(r['H_Fim'])], mode='lines', line=dict(color=c, width=40)))
            else:
                fig.add_trace(go.Scatter(x=[r['Cat']], y=[float(r['H'])], mode='markers+text', marker=dict(symbol='square', size=20, color=c), text=[r['Txt']], textposition="middle right"))
        
        fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=600, showlegend=False, dragmode=False)
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

# --- HISTÓRICO MENSAL (ABAIXO) ---
st.markdown("---")
if st.checkbox("Ver Histórico Completo"):
    st.dataframe(pd.DataFrame(st.session_state.dados), use_container_width=True)

if st.sidebar.button("🗑️ LIMPAR TUDO"):
    st.session_state.dados = []
    st.rerun()
