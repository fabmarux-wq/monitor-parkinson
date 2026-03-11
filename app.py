import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. Configuração de acessibilidade total
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# Estilo para botões GIGANTES e cores fortes
st.markdown("""
<style>
    .stButton > button { 
        height: 100px !important; font-size: 24px !important; 
        font-weight: bold !important; border-radius: 20px;
        margin-bottom: 15px; border: 3px solid #333 !important;
    }
</style>
""", unsafe_allow_stdio=True)

st.title("⏱️ Registro Instantâneo")

# 2. Memória Blindada (Session State)
if 'diario_parkinson' not in st.session_state:
    st.session_state['diario_parkinson'] = []

# FUNÇÃO DE SALVAMENTO: Registra na hora do clique
def clique_agora(cat, acao):
    agora = datetime.now()
    # Guardamos tudo como STRING (texto) para nunca dar TypeError
    novo = {
        "Data": agora.strftime("%d/%m/%Y"),
        "Hora": agora.strftime("%H:%M"),
        "Decimal": float(agora.hour + agora.minute/60),
        "Categoria": str(cat),
        "O_Que": str(acao),
        "Qtd": 1
    }
    st.session_state['diario_parkinson'].append(novo)
    st.toast(f"✅ {acao} registrado!")

# --- BOTÃO DE EMERGÊNCIA (DESTRAVAR) ---
if st.button("🛑 LIMPAR TUDO E DESTRAVAR", use_container_width=True):
    st.session_state['diario_parkinson'] = []
    st.rerun()

st.markdown("---")
st.write("### Toque no botão no momento exato:")

# --- BOTÕES DE UM CLIQUE ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 PROLOPA", use_container_width=True): clique_agora("Remédio", "Prolopa")
    if st.button("🟡 TREINO", use_container_width=True): clique_agora("Treino", "Exercício")
    if st.button("🫨 TREMOR", use_container_width=True): clique_agora("Sintoma", "Tremor")
with col2:
    if st.button("🔴 EM OFF", use_container_width=True): clique_agora("Estado", "Início OFF")
    if st.button("🔵 COMIDA", use_container_width=True): clique_agora("Comida", "Alimentação")
    if st.button("🧱 RIGIDEZ", use_container_width=True): clique_agora("Sintoma", "Rigidez")

st.markdown("---")

# --- GRÁFICOS (DIÁRIO E MENSAL) ---
if st.session_state['diario_parkinson']:
    df = pd.DataFrame(st.session_state['diario_parkinson'])
    
    tab1, tab2 = st.tabs(["📅 Gráfico de Hoje", "📈 Histórico Mensal"])
    
    with tab1:
        hoje = datetime.now().strftime("%d/%m/%Y")
        df_hoje = df[df['Data'] == hoje]
        if not df_hoje.empty:
            # Gráfico de hoje simples e fixo
            fig_dia = px.scatter(df_hoje, x="Categoria", y="Decimal", color="Categoria",
                                 text="Hora", height=500, title="Distribuição do Dia")
            fig_dia.update_traces(marker=dict(size=25))
            fig_dia.update_layout(yaxis=dict(range=[24, 0], dtick=1), showlegend=False)
            st.plotly_chart(fig_dia, use_container_width=True, config={'staticPlot': True})
        else:
            st.info("Aguardando o primeiro registro de hoje.")

    with tab2:
        st.write("### Evolução por Dia")
        # Gráfico que agrupa por dia para ver o mês
        fig_mes = px.bar(df, x="Data", y="Qtd", color="Categoria", title="Total de eventos no mês")
        st.plotly_chart(fig_mes, use_container_width=True)
        
        if st.checkbox("Ver lista de registros"):
            st.dataframe(df[["Data", "Hora", "Categoria", "O_Que"]], use_container_width=True)
else:
    st.info("Nada registrado ainda. Os gráficos aparecerão após o primeiro clique.")
