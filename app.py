import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração para celular
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# --- ESTILO DOS BOTÕES REDONDOS E CORES ---
st.markdown("""
<style>
    /* Diminuir o título */
    .titulo-pequeno { font-size: 20px !important; font-weight: bold; text-align: center; }
    
    /* Estilo para transformar botões em círculos/ovais coloridos */
    div.stButton > button {
        border-radius: 50px !important;
        height: 80px !important;
        width: 100% !important;
        font-size: 18px !important;
        font-weight: bold !important;
        color: white !important;
        border: none !important;
    }
    /* Cores específicas para cada botão */
    .stButton:nth-of-type(1) button { background-color: #198754 !important; } /* Verde - Remédio */
    .stButton:nth-of-type(2) button { background-color: #dc3545 !important; } /* Vermelho - OFF */
    .stButton:nth-of-type(3) button { background-color: #ffc107 !important; color: black !important; } /* Amarelo - Treino */
    .stButton:nth-of-type(4) button { background-color: #0dcaf0 !important; color: black !important; } /* Azul - Comida */
</style>
""", unsafe_allow_stdio=True)

st.markdown('<p class="titulo-pequeno">Monitor Parkinson Pro</p>', unsafe_allow_stdio=True)

if 'dados' not in st.session_state:
    st.session_state.dados = []
if 'aba_ativa' not in st.session_state:
    st.session_state.aba_ativa = None

# --- BOTÕES COLORIDOS E REDONDOS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("💊\nMed"): st.session_state.aba_ativa = "Medicação"
with col2:
    if st.button("⚠️\nOFF"): st.session_state.aba_ativa = "OFF"
with col3:
    if st.button("🏃\nExe"): st.session_state.aba_ativa = "Treino"
with col4:
    if st.button("🍽️\nAli"): st.session_state.aba_ativa = "Comida"

st.markdown("---")

# --- FORMULÁRIOS DE REGISTRO ---
if st.session_state.aba_ativa == "Medicação":
    st.subheader("💊 Registrar Remédios")
    h_m = st.time_input("Horário:", datetime.now().time())
    # Múltipla escolha voltou aqui:
    sel = st.multiselect("Selecione os remédios:", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
    if st.button("SALVAR DOSE"):
        for m in sel:
            num = m.split("(")[1].replace(")", "")
            st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_m.hour + (h_m.minute/60), "Cat": "Med", "Txt": num, "Tipo": "Ponto"})
        st.success("Registrado!")
        st.session_state.aba_ativa = None

elif st.session_state.aba_ativa == "OFF":
    st.subheader("⚠️ Registrar Período OFF")
    h_i = st.time_input("Início:", time(8, 0))
    h_f = st.time_input("Fim:", time(9, 0))
    if st.button("SALVAR ESTADO OFF"):
        st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_i.hour + (h_i.minute/60), "H_Fim": h_f.hour + (h_f.minute/60), "Cat": "OFF", "Txt": "!", "Tipo": "Periodo"})
        st.success("Registrado!")
        st.session_state.aba_ativa = None

elif st.session_state.aba_ativa == "Treino":
    st.subheader("🏃 Registrar Exercício")
    h_e = st.time_input("Horário:", datetime.now().time())
    exer = st.text_input("O que treinou? (ex: Caminhada)")
    if st.button("SALVAR TREINO"):
        st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_e.hour + (h_e.minute/60), "Cat": "Exe", "Txt": exer, "Tipo": "Ponto"})
        st.success("Treino salvo!")
        st.session_state.aba_ativa = None

elif st.session_state.aba_ativa == "Comida":
    st.subheader("🍽️ Registrar Alimentação")
    h_a = st.time_input("Horário:", datetime.now().time())
    refeicao = st.text_input("O que comeu?")
    if st.button("SALVAR COMIDA"):
        st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_a.hour + (h_a.minute/60), "Cat": "Ali", "Txt": refeicao, "Tipo": "Ponto"})
        st.success("Comida salva!")
        st.session_state.aba_ativa = None

# --- GRÁFICO DO DIA ---
if st.session_state.dados:
    df = pd.DataFrame(st.session_state.dados)
    hoje = str(datetime.now().date())
    df_h = df[df['Data'] == hoje]
    
    if not df_h.empty:
        st.write("### Seu dia hoje:")
        fig = go.Figure()
        for _, r in df_h.iterrows():
            cor = {"Med": "#198754", "OFF": "#dc3545", "Exe": "#ffc107", "Ali": "#0dcaf0"}.get(r['Cat'], "#000")
            if r.get('H_Fim'):
                fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['H'], r['H_Fim']], mode='lines+text', line=dict(color=cor, width=25), text=["", "OFF"]))
            else:
                fig.add_trace(go.Scatter(x=[r['Cat']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=18, color=cor), text=[r['Txt']], textposition="middle right", textfont=dict(size=18)))
        fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# Botão de exportar no final
if st.session_state.dados:
    csv = pd.DataFrame(st.session_state.dados).to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Dados para o Médico", data=csv, file_name='dados_parkinson.csv')
