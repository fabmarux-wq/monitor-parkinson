import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração para não dar erro no celular
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

st.markdown("### 📊 Monitor Parkinson Pro")

# Inicializa a memória de forma segura
if 'dados' not in st.session_state:
    st.session_state.dados = []
if 'menu' not in st.session_state:
    st.session_state.menu = None

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

st.markdown("---")

# --- FORMULÁRIOS ---
hoje_str = datetime.now().strftime("%Y-%m-%d")

if st.session_state.menu:
    # SELETOR DE 10 EM 10 MINUTOS
    if st.session_state.menu == "Med":
        st.subheader("💊 Registro de Remédios")
        h_m = st.time_input("Horário (10 em 10 min):", datetime.now().time(), step=600)
        sel = st.multiselect("Remédios (múltipla escolha):", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
        if st.button("SALVAR MEDICAÇÃO", use_container_width=True):
            for m in sel:
                n = m.split("(")[1].replace(")", "")
                st.session_state.dados.append({"Data": hoje_str, "H": h_m.hour + (h_m.minute/60), "Cat": "Med", "Txt": n, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "OFF":
        st.subheader("⚠️ Registro de OFF")
        sints = st.multiselect("Sintomas:", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
        col_i, col_f = st.columns(2)
        with col_i: h_i = st.time_input("Início:", time(8, 0), step=600)
        with col_f: h_f = st.time_input("Fim:", time(8, 30), step=600)
        if st.button("SALVAR ESTADO OFF", use_container_width=True):
            txt = ", ".join(sints) if sints else "OFF"
            st.session_state.dados.append({"Data": hoje_str, "H": h_i.hour + (h_i.minute/60), "H_Fim": h_f.hour + (h_f.minute/60), "Cat": "OFF", "Txt": txt, "Tipo": "Periodo"})
            st.session_state.menu = None
            st.rerun()

    if st.button("Fechar"):
        st.session_state.menu = None
        st.rerun()

# --- VISUALIZAÇÃO ---
tab1, tab2 = st.tabs(["📅 Hoje", "📅 Histórico"])

with tab1:
    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)
        # Filtro de data seguro contra TypeError
        df_h = df[df['Data'] == hoje_str]
        
        if not df_h.empty:
            fig = go.Figure()
            cores = {"Med": "#198754", "OFF": "#dc3545", "Exe": "#ffc107", "Ali": "#0dcaf0"}
            for _, r in df_h.iterrows():
                c = cores.get(r['Cat'], "#000")
                if 'H_Fim' in r and not pd.isna(r['H_Fim']):
                    fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['H'], r['H_Fim']], mode='lines', line=dict(color=c, width=40)))
                else:
                    fig.add_trace(go.Scatter(x=[r['Cat']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=20, color=c), text=[r['Txt']], textposition="middle right", textfont=dict(size=18)))
            
            # GRÁFICO FIXO (SEM ZOOM PARA NÃO SUMIR)
            fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=600, showlegend=False, dragmode=False)
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
        else:
            st.write("Sem registros hoje.")

with tab2:
    if st.session_state.dados:
        st.dataframe(pd.DataFrame(st.session_state.dados), use_container_width=True)

# Botão para limpar testes (na lateral)
if st.sidebar.button("Zerar Aplicativo"):
    st.session_state.dados = []
    st.rerun()
