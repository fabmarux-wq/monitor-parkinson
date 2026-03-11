import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(page_title="Monitor Parkinson", layout="wide")

# --- ESTILO PARA LETRAS GIGANTES ---
st.markdown("""
<style>
    /* Aumenta a letra das ABAS */
    .stTabs [data-baseweb="tab"] p {
        font-size: 26px !important;
        font-weight: bold !important;
    }
    /* Aumenta a letra das CATEGORIAS na lateral */
    .stRadio [data-testid="stMarkdownContainer"] p {
        font-size: 26px !important;
        font-weight: bold !important;
    }
    /* Aumenta o texto dos botões */
    .stButton button p {
        font-size: 24px !important;
        font-weight: bold !important;
    }
    /* Aumenta os rótulos de tempo e seleção */
    label {
        font-size: 22px !important;
    }
</style>
""", unsafe_allow_stdio=True)

st.title("📊 Monitor Parkinson Pro")

if 'dados' not in st.session_state:
    st.session_state.dados = []

# Configurações
CORES = {"Medicação": "#198754", "Estado 'Off'": "#dc3545", "Exercício": "#ffc107", "Alimentação": "#0dcaf0"}
MAPA_MED = {"Prolopa BD": "1", "Mantidan": "2", "Pramipexol": "3", "Rasagilina": "4", "Prolopa HBS": "5", "Prolopa D": "6"}
MAPA_OFF = {"Tremor": "1", "Congelamento": "2"}

# --- MENU LATERAL (REGISTRO) ---
st.sidebar.header("📝 REGISTRO")
data_reg = st.sidebar.date_input("Data", datetime.now())
cat = st.sidebar.radio("Selecione:", ["Medicação", "Estado 'Off'", "Exercício", "Alimentação"])

if cat == "Estado 'Off'":
    h_i = st.sidebar.time_input("Início", time(8, 0))
    h_f = st.sidebar.time_input("Fim", time(9, 0))
    sints = st.sidebar.multiselect("Sintomas:", ["Tremor", "Congelamento"])
    if st.sidebar.button("SALVAR REGISTRO"):
        cods = [MAPA_OFF[s] for s in sints]
        st.session_state.dados.append({"Data": str(data_reg), "H": h_i.hour + (h_i.minute/60), "H_Fim": h_f.hour + (h_f.minute/60), "Cat": cat, "Txt": ", ".join(cods), "Tipo": "Periodo"})
        st.sidebar.success("Salvo!")

elif cat == "Medicação":
    h_m = st.sidebar.time_input("Horário", datetime.now().time())
    sel = st.sidebar.multiselect("Remédios:", list(MAPA_MED.keys()))
    if st.sidebar.button("SALVAR DOSE"):
        h_dec = h_m.hour + (h_m.minute/60)
        for i, m in enumerate(sel):
            st.session_state.dados.append({"Data": str(data_reg), "H": h_dec, "H_Fim": None, "Cat": cat, "Txt": MAPA_MED[m], "Tipo": "Ponto", "Shift": i * 0.15})
        st.sidebar.success("Salvo!")
else:
    h_out = st.sidebar.time_input("Horário", datetime.now().time())
    desc = st.sidebar.text_input("Descrição:")
    if st.sidebar.button("SALVAR"):
        st.session_state.dados.append({"Data": str(data_reg), "H": h_out.hour + (h_out.minute/60), "H_Fim": None, "Cat": cat, "Txt": desc, "Tipo": "Ponto", "Shift": 0})
        st.sidebar.success("Salvo!")

# --- AS ABAS COM LETRAS GRANDES ---
tab_dia, tab_med, tab_off, tab_exe, tab_ali = st.tabs(["📅 Diário", "💊 Medicação", "⚠️ Off", "🏃 Exercício", "🍽️ Alimentação"])

if st.session_state.dados:
    df = pd.DataFrame(st.session_state.dados)
    df['Data'] = pd.to_datetime(df['Data']).dt.date
    
    with tab_dia:
        df_d = df[df['Data'] == data_reg]
        if not df_d.empty:
            fig = go.Figure()
            for _, r in df_d.iterrows():
                if r['Tipo'] == "Periodo":
                    fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['H'], r['H_Fim']], mode='lines+markers+text', line=dict(color=CORES[r['Cat']], width=20), text=["", r['Txt']], textposition="middle right", textfont=dict(size=20)))
                else:
                    fig.add_trace(go.Scatter(x=[r['Cat']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=20, color=CORES[r['Cat']]), text=[r['Txt']], textposition="middle right", textfont=dict(size=20)))
            fig.update_layout(yaxis=dict(range=[24, 0], dtick=1, tickfont=dict(size=18)), height=800, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado hoje.")

    def mostrar_aba(nome_cat):
        df_c = df[df['Cat'] == nome_cat]
        if not df_c.empty:
            fig_c = go.Figure()
            for _, r in df_c.iterrows():
                fig_c.add_trace(go.Scatter(x=[r['Data']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=18, color=CORES[nome_cat]), text=[r['Txt']], textposition="middle right", textfont=dict(size=18)))
            fig_c.update_layout(yaxis=dict(range=[24, 0], dtick=2, tickfont=dict(size=16)), height=500, showlegend=False)
            st.plotly_chart(fig_c, use_container_width=True)

    with tab_med: mostrar_aba("Medicação")
    with tab_off: mostrar_aba("Estado 'Off'")
    with tab_exe: mostrar_aba("Exercício")
    with tab_ali: mostrar_aba("Alimentação")

    # Botão de Exportar
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Baixar Excel", data=csv, file_name='dados_parkinson.csv')
else:
    st.info("💡 Registre algo na lateral para ativar os gráficos.")
