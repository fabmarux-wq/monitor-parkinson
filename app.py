import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração para o celular
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

st.title("📊 Monitor Parkinson Pro")

# Memória do App
if 'dados' not in st.session_state:
    st.session_state.dados = []

# --- BOTÕES DE CATEGORIA GRANDES ---
st.write("### 1. Escolha o que registrar:")

# Criando botões grandes usando colunas
col1, col2 = st.columns(2)
with col1:
    btn_med = st.button("💊 REMÉDIO", use_container_width=True)
with col2:
    btn_off = st.button("⚠️ OFF", use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    btn_exe = st.button("🏃 TREINO", use_container_width=True)
with col4:
    btn_ali = st.button("🍽️ COMIDA", use_container_width=True)

# Controla qual formulário aparece
if 'form' not in st.session_state: st.session_state.form = None
if btn_med: st.session_state.form = "Medicação"
if btn_off: st.session_state.form = "OFF"
if btn_exe: st.session_state.form = "Exercício"
if btn_ali: st.session_state.form = "Alimentação"

st.markdown("---")

# --- FORMULÁRIOS DE REGISTRO ---
if st.session_state.form == "Medicação":
    st.subheader("💊 REGISTRAR REMÉDIO")
    h_m = st.time_input("Que horas?", datetime.now().time())
    remedio = st.selectbox("Qual remédio?", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
    if st.button("CONFIRMAR DOSE", use_container_width=True):
        num = remedio.split("(")[1].replace(")", "")
        st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_m.hour + (h_m.minute/60), "Cat": "Medicação", "Txt": num, "Tipo": "Ponto"})
        st.success("Salvo!")
        st.session_state.form = None

elif st.session_state.form == "OFF":
    st.subheader("⚠️ REGISTRAR ESTADO OFF")
    h_i = st.time_input("Início:", time(8, 0))
    h_f = st.time_input("Fim:", time(9, 0))
    if st.button("CONFIRMAR OFF", use_container_width=True):
        st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_i.hour + (h_i.minute/60), "H_Fim": h_f.hour + (h_f.minute/60), "Cat": "OFF", "Txt": "!", "Tipo": "Periodo"})
        st.success("Salvo!")
        st.session_state.form = None

# --- ABAS DE VISUALIZAÇÃO ---
st.write("### 2. Seus Gráficos:")
tab1, tab2 = st.tabs(["📅 DIA", "📈 TUDO"])

with tab1:
    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)
        fig = go.Figure()
        for _, r in df.iterrows():
            if r.get('H_Fim'):
                fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['H'], r['H_Fim']], mode='lines+text', line=dict(color="#dc3545", width=25), text=["", "OFF"]))
            else:
                fig.add_trace(go.Scatter(x=[r['Cat']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=20, color="#198754"), text=[r['Txt']], textposition="middle right", textfont=dict(size=20)))
        fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nada registrado hoje.")

with tab2:
    if st.session_state.dados:
        st.dataframe(pd.DataFrame(st.session_state.dados)[['Data', 'Cat', 'Txt']], use_container_width=True)
