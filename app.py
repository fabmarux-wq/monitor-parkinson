import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Configuração para evitar erros de visualização no celular
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

st.markdown("### 📊 Monitor Parkinson Pro")

# --- MEMÓRIA ---
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

hoje_str = datetime.now().strftime("%Y-%m-%d")

# --- FORMULÁRIOS COM SELEÇÃO DE HORA MANUAL (NÃO TRAVA) ---
if st.session_state.menu:
    st.info(f"Registrando: {st.session_state.menu}")
    
    # Seleção de hora e minuto separada para evitar travamento do relógio
    col_h, col_m = st.columns(2)
    with col_h:
        h_sel = st.selectbox("Hora:", list(range(24)), index=datetime.now().hour)
    with col_m:
        # Pula de 10 em 10 minutos
        m_sel = st.selectbox("Minuto:", [0, 10, 20, 30, 40, 50], index=0)
    
    h_dec = float(h_sel + m_sel/60)

    if st.session_state.menu == "Med":
        sel = st.multiselect("Remédios:", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
        if st.button("SALVAR MEDICAÇÃO", use_container_width=True):
            for m in sel:
                n = m.split("(")[1].replace(")", "")
                st.session_state.dados.append({"Data": hoje_str, "H": h_dec, "Cat": "Med", "Txt": n, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "OFF":
        sints = st.multiselect("Sintomas (Múltiplos):", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
        st.write("Horário de Término:")
        col_hf, col_mf = st.columns(2)
        with col_hf: h_f = st.selectbox("Hora Fim:", list(range(24)), index=h_sel)
        with col_mf: m_f = st.selectbox("Min Fim:", [0, 10, 20, 30, 40, 50], index=min(5, (m_sel//10)+1))
        
        if st.button("SALVAR ESTADO OFF", use_container_width=True):
            t = ", ".join(sints) if sints else "OFF"
            st.session_state.dados.append({
                "Data": hoje_str, "H": h_dec, 
                "H_Fim": float(h_f + m_f/60), 
                "Cat": "OFF", "Txt": t, "Tipo": "Periodo"
            })
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Exe":
        txt_exe = st.text_input("Atividade (Ex: Fisioterapia):")
        if st.button("SALVAR EXERCÍCIO", use_container_width=True):
            st.session_state.dados.append({"Data": hoje_str, "H": h_dec, "Cat": "Exe", "Txt": txt_exe, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Ali":
        txt_ali = st.text_input("Refeição (Ex: Almoço):")
        if st.button("SALVAR ALIMENTAÇÃO", use_container_width=True):
            st.session_state.dados.append({"Data": hoje_str, "H": h_dec, "Cat": "Ali", "Txt": txt_ali, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    if st.button("Fechar ❌"):
        st.session_state.menu = None
        st.rerun()

# --- GRÁFICO DIÁRIO FIXO ---
if st.session_state.dados:
    df = pd.DataFrame(st.session_state.dados)
    df_h = df[df['Data'] == hoje_str]
    
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

# --- LIM
