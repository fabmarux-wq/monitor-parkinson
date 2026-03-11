import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Configuração focada em rapidez e facilidade
st.set_page_config(page_title="Registro Rápido", layout="centered")

# Estilo: Botões GIGANTES para facilitar o toque
st.markdown("""
<style>
    .stButton > button { 
        height: 100px !important; 
        font-size: 25px !important; 
        font-weight: bold !important; 
        border-radius: 20px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_stdio=True)

st.title("⏱️ Registro Instantâneo")

# Inicializa a memória
if 'dados' not in st.session_state:
    st.session_state.dados = []

# Função para salvar no instante do clique
def salvar(categoria, texto):
    agora = datetime.now()
    h_dec = float(agora.hour + agora.minute/60)
    data_txt = agora.strftime("%d/%m/%Y")
    hora_txt = agora.strftime("%H:%M")
    st.session_state.dados.append({
        "Data": data_txt, 
        "H": h_dec, 
        "Hora": hora_txt,
        "Cat": categoria, 
        "Txt": texto
    })
    st.toast(f"Registrado às {hora_txt}!")

# --- BOTÕES INSTANTÂNEOS ---
st.write("### Clique para registrar AGORA:")

col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 TOMOU\nPROLOPA", use_container_width=True):
        salvar("Med", "Prolopa")
    if st.button("🟡 TREINOU\nAGORA", use_container_width=True):
        salvar("Exe", "Exercício")

with col2:
    if st.button("🔴 ENTROU\nEM OFF", use_container_width=True):
        salvar("OFF", "Início OFF")
    if st.button("🔵 COMEU\nAGORA", use_container_width=True):
        salvar("Ali", "Alimentação")

# --- ÁREA DE SINTOMAS (Múltipla escolha rápida) ---
st.markdown("---")
st.write("### Sintomas no momento:")
sints = st.multiselect("Marque e clique no botão abaixo:", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
if st.button("💾 SALVAR SINTOMAS SELECIONADOS", use_container_width=True):
    txt_s = ", ".join(sints) if sints else "Sintomas"
    salvar("Sint", txt_s)

# --- GRÁFICO DO DIA (ESTÁTICO) ---
if st.session_state.dados:
    st.markdown("---")
    st.write("### Seu dia até agora:")
    df = pd.DataFrame(st.session_state.dados)
    
    fig = go.Figure()
    cores = {"Med": "#198754", "OFF": "#dc3545", "Exe": "#ffc107", "Ali": "#0dcaf0", "Sint": "#6f42c1"}
    
    for _, r in df.iterrows():
        c = cores.get(r['Cat'], "#000")
        fig.add_trace(go.Scatter(
            x=[r['Cat']], y=[float(r['H'])], 
            mode='markers+text', 
            marker=dict(size=25, color=c),
            text=[f"{r['Hora']} - {r['Txt']}"],
            textposition="middle right"
        ))
    
    fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=500, showlegend=False, dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

# Opção de limpar se precisar
if st.sidebar.button("Zerar Tudo"):
    st.session_state.dados = []
    st.rerun()
