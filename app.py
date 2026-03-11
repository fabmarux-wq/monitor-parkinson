import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

st.set_page_config(page_title="Monitor Parkinson", layout="wide")
st.title("📊 Painel Parkinson Pro")

if 'dados' not in st.session_state:
    st.session_state.dados = []

# Configurações de Cores e Números
CORES = {"Medicação": "#198754", "Estado 'Off'": "#dc3545", "Exercício": "#ffc107", "Alimentação": "#0dcaf0"}
MAPA_MED = {"Prolopa BD": "1", "Mantidan": "2", "Pramipexol": "3", "Rasagilina": "4", "Prolopa HBS": "5", "Prolopa D": "6"}
MAPA_OFF = {"Tremor": "1", "Congelamento": "2"}

# Menu Lateral
st.sidebar.header("📝 Registro")
cat = st.sidebar.radio("Categoria:", ["Medicação", "Estado 'Off'", "Exercício", "Alimentação"])

if cat == "Estado 'Off'":
    h_i = st.sidebar.time_input("Início", time(8, 0))
    h_f = st.sidebar.time_input("Fim", time(9, 0))
    sints = st.sidebar.multiselect("Sintomas:", ["Tremor", "Congelamento"])
    if st.sidebar.button("Salvar OFF"):
        cods = [MAPA_OFF[s] for s in sints]
        st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_i.hour + (h_i.minute/60), "H_Fim": h_f.hour + (h_f.minute/60), "Cat": cat, "Txt": ", ".join(cods), "Tipo": "Periodo"})
        st.success("OFF Salvo!")

elif cat == "Medicação":
    h_m = st.sidebar.time_input("Horário", datetime.now().time())
    sel = st.sidebar.multiselect("Remédios:", list(MAPA_MED.keys()))
    if st.sidebar.button("Salvar Medicação"):
        for m in sel:
            st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_m.hour + (h_m.minute/60), "H_Fim": None, "Cat": cat, "Txt": MAPA_MED[m], "Tipo": "Ponto"})
        st.success("Medicação Salva!")
else:
    h_out = st.sidebar.time_input("Horário", datetime.now().time())
    desc = st.sidebar.text_input("Descrição:")
    if st.sidebar.button("Salvar Registro"):
        st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_out.hour + (h_out.minute/60), "H_Fim": None, "Cat": cat, "Txt": desc, "Tipo": "Ponto"})
        st.success("Salvo!")

# Exibição do Gráfico
if st.session_state.dados:
    df = pd.DataFrame(st.session_state.dados)
    fig = go.Figure()
    for _, r in df.iterrows():
        if r['Tipo'] == "Periodo":
            fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['H'], r['H_Fim']], mode='lines+markers+text', line=dict(color=CORES[r['Cat']], width=15), text=["", r['Txt']], textposition="middle right"))
        else:
            fig.add_trace(go.Scatter(x=[r['Cat']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=15, color=CORES[r['Cat']]), text=[r['Txt']], textposition="middle right"))
    
    fig.update_layout(yaxis=dict(range=[24, 0], dtick=1, title="Horas"), height=700, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Exportar CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Planilha", data=csv, file_name='dados_parkinson.csv', mime='text/csv')
else:
    st.info("💡 Registre algo para ver o gráfico aparecer.")
