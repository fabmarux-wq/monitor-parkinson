import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração Básica
st.set_page_config(page_title="Monitor Parkinson", layout="wide")

# ESTILO PARA AUMENTAR AS LETRAS - VERSÃO SEGURA
st.markdown("""
<style>
    /* Aumenta a letra das ABAS no topo */
    button[data-baseweb="tab"] p {
        font-size: 28px !important;
        font-weight: bold !important;
    }
    /* Aumenta a letra das categorias (Medicação, Off...) */
    .stRadio [data-testid="stMarkdownContainer"] p {
        font-size: 28px !important;
        font-weight: bold !important;
    }
    /* Aumenta o texto dos botões de Salvar */
    .stButton button p {
        font-size: 26px !important;
    }
</style>
""", unsafe_allow_stdio=True)

st.title("📊 Monitor Parkinson Pro")

# Inicializa a memória do app
if 'dados' not in st.session_state:
    st.session_state.dados = []

# Mapas de cores e números
CORES = {"Medicação": "#198754", "Estado 'Off'": "#dc3545", "Exercício": "#ffc107", "Alimentação": "#0dcaf0"}
MAPA_MED = {"Prolopa BD": "1", "Mantidan": "2", "Pramipexol": "3", "Rasagilina": "4", "Prolopa HBS": "5", "Prolopa D": "6"}

# --- REGISTRO NA LATERAL ---
st.sidebar.header("📝 REGISTRO")
cat = st.sidebar.radio("Escolha:", ["Medicação", "Estado 'Off'", "Exercício", "Alimentação"])

if cat == "Medicação":
    h_m = st.sidebar.time_input("Horário", datetime.now().time())
    sel = st.sidebar.multiselect("Remédios:", list(MAPA_MED.keys()))
    if st.sidebar.button("SALVAR DOSE"):
        for m in sel:
            st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_m.hour + (h_m.minute/60), "Cat": cat, "Txt": MAPA_MED[m], "Tipo": "Ponto"})
        st.sidebar.success("Salvo!")

elif cat == "Estado 'Off'":
    h_i = st.sidebar.time_input("Início", time(8, 0))
    h_f = st.sidebar.time_input("Fim", time(9, 0))
    if st.sidebar.button("SALVAR OFF"):
        st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_i.hour + (h_i.minute/60), "H_Fim": h_f.hour + (h_f.minute/60), "Cat": cat, "Txt": "!", "Tipo": "Periodo"})
        st.sidebar.success("Salvo!")

# --- AS ABAS COM LETRAS GRANDES ---
tab_dia, tab_med, tab_off, tab_exe, tab_ali = st.tabs(["📅 Diário", "💊 Medicação", "⚠️ Off", "🏃 Exercício", "🍽️ Alimentação"])

if st.session_state.dados:
    df = pd.DataFrame(st.session_state.dados)
    
    with tab_dia:
        fig = go.Figure()
        for _, r in df.iterrows():
            cor = CORES.get(r['Cat'], "#000")
            if r.get('H_Fim'):
                fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['H'], r['H_Fim']], mode='lines+text', line=dict(color=cor, width=20), text=["", "OFF"]))
            else:
                fig.add_trace(go.Scatter(x=[r['Cat']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=18, color=cor), text=[r['Txt']], textposition="middle right", textfont=dict(size=20)))
        fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=700, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Botão de exportar
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Baixar Excel", data=csv, file_name='dados.csv')
else:
    st.info("💡 Use a lateral para registrar algo.")
