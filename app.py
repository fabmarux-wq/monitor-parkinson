import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração de sobrevivência para o Android
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

st.markdown("### 📊 Monitor Parkinson Pro")

# --- MEMÓRIA À PROVA DE ERROS ---
if 'dados' not in st.session_state:
    st.session_state.dados = []

# Função para converter tudo em número e evitar TypeError
def p_num(valor):
    try: return float(valor)
    except: return 0.0

# --- BOTÕES DE REGISTRO ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🟢\nMED", use_container_width=True): st.session_state.menu = "Med"
with c2:
    if st.button("🔴\nOFF", use_container_width=True): st.session_state.menu = "OFF"
with c3:
    if st.button("🟡\nEXE", use_container_width=True): st.session_state.menu = "Exe"
with c4:
    if st.button("🔵\nALI", use_container_width=True): st.session_state.menu = "Ali"

# --- FORMULÁRIOS ---
if 'menu' in st.session_state and st.session_state.menu:
    st.divider()
    # Horário fixo em 10 em 10 minutos
    h_escolha = st.time_input("Horário (10 em 10 min):", datetime.now().time(), step=600)
    h_dec = p_num(h_escolha.hour + h_escolha.minute/60)
    hoje = datetime.now().strftime("%d/%m/%Y")

    if st.session_state.menu == "Med":
        sel = st.multiselect("Remédios:", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
        if st.button("SALVAR"):
            for m in sel:
                n = m.split("(")[1].replace(")", "")
                st.session_state.dados.append({"Data": hoje, "H": h_dec, "Cat": "Med", "Txt": n})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "OFF":
        sints = st.multiselect("Sintomas:", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
        h_fim = st.time_input("Fim do OFF:", h_escolha, step=600)
        if st.button("SALVAR OFF"):
            t = ", ".join(sints) if sints else "OFF"
            st.session_state.dados.append({"Data": hoje, "H": h_dec, "H_Fim": p_num(h_fim.hour + h_fim.minute/60), "Cat": "OFF", "Txt": t})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Exe":
        txt_e = st.text_input("Atividade:")
        if st.button("SALVAR TREINO"):
            st.session_state.dados.append({"Data": hoje, "H": h_dec, "Cat": "Exe", "Txt": txt_e})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Ali":
        txt_a = st.text_input("O que comeu?")
        if st.button("SALVAR COMIDA"):
            st.session_state.dados.append({"Data": hoje, "H": h_dec, "Cat": "Ali", "Txt": txt_a})
            st.session_state.menu = None
            st.rerun()

    if st.button("Cancelar ❌"):
        st.session_state.menu = None
        st.rerun()

# --- GRÁFICO ESTÁTICO (FIXO) ---
st.divider()
if st.session_state.dados:
    try:
        df = pd.DataFrame(st.session_state.dados)
        fig = go.Figure()
        cores = {"Med": "#198754", "OFF": "#dc3545", "Exe": "#ffc107", "Ali": "#0dcaf0"}
        
        for _, r in df.iterrows():
            c = cores.get(r['Cat'], "#000")
            if 'H_Fim' in r and not pd.isna(r['H_Fim']):
                fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[p_num(r['H']), p_num(r['H_Fim'])], mode='lines', line=dict(color=c, width=40)))
            else:
                fig.add_trace(go.Scatter(x=[r['Cat']], y=[p_num(r['H'])], mode='markers+text', marker=dict(symbol='square', size=20, color=c), text=[r['Txt']], textposition="middle right"))
        
        fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=600, showlegend=False, dragmode=False)
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    except:
        st.error("Erro nos dados. Clique no botão abaixo para resetar.")

if st.button("🗑️ LIMPAR TUDO (Reset)"):
    st.session_state.dados = []
    st.session_state.menu = None
    st.rerun()
