import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração para Celular
st.set_page_config(page_title="Monitor Parkinson", layout="wide")
st.title("📊 Painel Parkinson Pro")

# Inicializa a memória
if 'dados' not in st.session_state:
    st.session_state.dados = []

# Configurações de Cores e Números
CORES = {"Medicação": "#198754", "Estado 'Off'": "#dc3545", "Exercício": "#ffc107", "Alimentação": "#0dcaf0"}
MAPA_MED = {"Prolopa BD": "1", "Mantidan": "2", "Pramipexol": "3", "Rasagilina": "4", "Prolopa HBS": "5", "Prolopa D": "6"}
MAPA_OFF = {"Tremor": "1", "Congelamento": "2"}

# --- MENU LATERAL ---
st.sidebar.header("📝 Registro")
data_reg = st.sidebar.date_input("Data do Evento", datetime.now())
cat = st.sidebar.radio("Escolha a Categoria:", ["Medicação", "Estado 'Off'", "Exercício", "Alimentação"])

if cat == "Estado 'Off'":
    h_i = st.sidebar.time_input("Início do OFF", time(8, 0))
    h_f = st.sidebar.time_input("Término do OFF", time(9, 0))
    sints = st.sidebar.multiselect("Sintomas:", ["Tremor", "Congelamento"])
    if st.sidebar.button("Salvar OFF"):
        cods = [MAPA_OFF[s] for s in sints]
        st.session_state.dados.append({"Data": str(data_reg), "H": h_i.hour + (h_i.minute/60), "H_Fim": h_f.hour + (h_f.minute/60), "Cat": cat, "Txt": ", ".join(cods), "Tipo": "Periodo"})
        st.sidebar.success("OFF Salvo!")

elif cat == "Medicação":
    h_m = st.sidebar.time_input("Horário da Dose", datetime.now().time())
    sel = st.sidebar.multiselect("Remédios Tomados:", list(MAPA_MED.keys()))
    if st.sidebar.button("Salvar Medicação"):
        h_dec = h_m.hour + (h_m.minute/60)
        for i, m in enumerate(sel):
            st.session_state.dados.append({"Data": str(data_reg), "H": h_dec, "H_Fim": None, "Cat": cat, "Txt": MAPA_MED[m], "Tipo": "Ponto"})
        st.sidebar.success("Medicação Salva!")
else:
    h_out = st.sidebar.time_input("Horário", datetime.now().time())
    desc = st.sidebar.text_input("O que aconteceu?")
    if st.sidebar.button("Salvar Registro"):
        st.session_state.dados.append({"Data": str(data_reg), "H": h_out.hour + (h_out.minute/60), "H_Fim": None, "Cat": cat, "Txt": desc, "Tipo": "Ponto"})
        st.sidebar.success("Registro Salvo!")

# --- ABAS ---
tab_dia, tab_med, tab_off, tab_exe, tab_ali = st.tabs(["📅 Diário", "💊 Medicação", "⚠️ Off", "🏃 Exercício", "🍽️ Alimentação"])

if st.session_state.dados:
    df = pd.DataFrame(st.session_state.dados)
    df['Data'] = pd.to_datetime(df['Data']).dt.date
    
    with tab_dia:
        dia_f = st.date_input("Ver dia:", data_reg, key="dia_f")
        df_d = df[df['Data'] == dia_f]
        if not df_d.empty:
            fig = go.Figure()
            for _, r in df_d.iterrows():
                if r['Tipo'] == "Periodo":
                    fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['H'], r['H_Fim']], mode='lines+markers+text', line=dict(color=CORES[r['Cat']], width=15), text=["", r['Txt']], textposition="middle right"))
                else:
                    fig.add_trace(go.Scatter(x=[r['Cat']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=15, color=CORES[r['Cat']]), text=[r['Txt']], textposition="middle right"))
            fig.update_layout(yaxis=dict(range=[24, 0], dtick=1, title="Horas"), height=700, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    def mostrar_aba(nome_cat):
        df_c = df[df['Cat'] == nome_cat]
        if not df_c.empty:
            fig_c = go.Figure()
            for _, r in df_c.iterrows():
                fig_c.add_trace(go.Scatter(x=[r['Data']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=12, color=CORES[nome_cat]), text=[r['Txt']], textposition="middle right"))
            fig_c.update_layout(yaxis=dict(range=[24, 0], dtick=2), height=500, showlegend=False)
            st.plotly_chart(fig_c, use_container_width=True)
    
    with tab_med: mostrar_aba("Medicação")
    with tab_off: mostrar_aba("Estado 'Off'")
    with tab_exe: mostrar_aba("Exercício")
    with tab_ali: mostrar_aba("Alimentação")
else:
    st.info("💡 Use a lateral para registrar algo. As abas aparecerão com dados assim que você salvar o primeiro evento.")
