import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(page_title="Monitor Parkinson Pro", layout="wide")
st.title("📊 Painel de Controle de Saúde")

# Inicializa a memória se estiver vazia
if 'dados' not in st.session_state:
    st.session_state.dados = []

# --- CONFIGURAÇÕES ---
CORES = {"Medicação": "#198754", "Estado 'Off'": "#dc3545", "Exercício": "#ffc107", "Alimentação": "#0dcaf0"}

# Seus números definidos para os remédios e sintomas
MAPA_MED = {
    "Prolopa BD": "1", "Mantidan": "2", "Pramipexol": "3", 
    "Rasagilina": "4", "Prolopa HBS": "5", "Prolopa D": "6"
}
MAPA_OFF = {"Tremor": "1", "Congelamento": "2"}

# --- BARRA LATERAL ---
st.sidebar.header("📝 Registro")
data_reg = st.sidebar.date_input("Data", datetime.now())
categoria = st.sidebar.radio("Categoria:", ["Medicação", "Estado 'Off'", "Exercício", "Alimentação"])

if categoria == "Estado 'Off'":
    h_ini = st.sidebar.time_input("Início", time(8, 0))
    h_fim = st.sidebar.time_input("Fim", time(9, 0))
    sintomas = st.sidebar.multiselect("Sintomas:", ["Tremor", "Congelamento"])
    if st.sidebar.button("Salvar OFF"):
        codigos = [MAPA_OFF[s] for s in sintomas]
        st.session_state.dados.append({
            "Data": str(data_reg), "H": h_ini.hour + (h_ini.minute/60), "H_Fim": h_fim.hour + (h_fim.minute/60),
            "Cat": categoria, "Txt": ", ".join(codigos), "Tipo": "Periodo", "Shift": 0
        })
        st.sidebar.success("OFF salvo!")

elif categoria == "Medicação":
    h_med = st.sidebar.time_input("Horário", datetime.now().time())
    selecionados = st.sidebar.multiselect("Remédios:", list(MAPA_MED.keys()))
    if st.sidebar.button("Salvar Medicação"):
        h_dec = h_med.hour + (h_med.minute/60)
        for i, m in enumerate(selecionados):
            st.session_state.dados.append({
                "Data": str(data_reg), "H": h_dec, "H_Fim": None,
                "Cat": categoria, "Txt": MAPA_MED[m], "Tipo": "Ponto", "Shift": i * 0.15 
            })
        st.sidebar.success("Medicação salva!")
else:
    h_out = st.sidebar.time_input("Horário", datetime.now().time())
    desc = st.sidebar.text_input("Descrição:")
    if st.sidebar.button("Salvar Registro"):
        st.session_state.dados.append({
            "Data": str(data_reg), "H": h_out.hour + (h_out.minute/60), "H_Fim": None,
            "Cat": categoria, "Txt": desc, "Tipo": "Ponto", "Shift": 0
        })

# --- BOTÃO EXPORTAR ---
st.sidebar.markdown("---")
if st.session_state.dados:
    df_export = pd.DataFrame(st.session_state.dados)
    csv = df_export.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Baixar Planilha Excel (CSV)",
        data=csv,
        file_name=f'parkinson_{data_reg}.csv',
        mime='text/csv',
    )

# --- VISUALIZAÇÃO ---
if st.session_state.dados:
    df = pd.DataFrame(st.session_state.dados)
    df['Data'] = pd.to_datetime(df['Data']).dt.date
    tab_dia, tab_med, tab_off, tab_exe, tab_ali = st.tabs(["📅 Diário", "💊 Medicação", "⚠️ Off", "🏃 Exercício", "🍽️ Alimentação"])

    with tab_dia:
        dia_f = st.date_input("Ver dia:", data_reg, key="dia_f")
        df_d = df[df['Data'] == dia_f]
        fig = go.Figure()
        for _, r in df_d.iterrows():
            if r['Tipo'] == "Periodo":
                fig.add_trace(go.Scatter(
                    x=[r['Cat'], r['Cat']], y=[r['H'], r['H_Fim']],
                    mode='lines+markers+text', line=dict(color=CORES[r['Cat']], width=15),
                    text=["", r['Txt']], textposition="middle right"
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=[r['Cat']], y=[r['H']], mode='markers+text',
                    marker=
