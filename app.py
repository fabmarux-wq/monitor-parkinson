import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Configuração focada em acessibilidade
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# Estilo: Botões GIGANTES e cores fortes
st.markdown("""
<style>
    .stButton > button { 
        height: 100px !important; font-size: 24px !important; 
        font-weight: bold !important; border-radius: 20px;
        margin-bottom: 15px; border: 3px solid #333 !important;
    }
    .stTabs [data-baseweb="tab"] p { font-size: 22px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_stdio=True)

st.title("⏱️ Registro Instantâneo")

# 1. Memória Blindada (Session State)
if 'diario_v3' not in st.session_state:
    st.session_state['diario_v3'] = []

# FUNÇÃO DE SALVAMENTO: Registra na hora exata do clique
def registrar_clique(categoria, acao):
    agora = datetime.now()
    # Guardamos tudo como texto (string) ou número puro (float) para nunca dar TypeError
    novo_item = {
        "Data": agora.strftime("%d/%m/%Y"),
        "Hora": agora.strftime("%H:%M"),
        "Decimal": float(agora.hour + agora.minute/60),
        "Categoria": str(categoria),
        "Descricao": str(acao),
        "Contagem": 1
    }
    st.session_state['diario_v3'].append(novo_item)
    st.toast(f"✅ {acao} salvo!")

# --- BOTÃO DE EMERGÊNCIA (PARA DESTRAVAR O APP) ---
if st.button("🛑 LIMPAR TUDO (USAR SE DER ERRO)", use_container_width=True):
    st.session_state['diario_v3'] = []
    st.rerun()

st.markdown("---")

# --- BOTÕES DE UM CLIQUE ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 PROLOPA", use_container_width=True): registrar_clique("Remédio", "Prolopa")
    if st.button("🟡 TREINO", use_container_width=True): registrar_clique("Atividade", "Exercício")
    if st.button("🫨 TREMOR", use_container_width=True): registrar_clique("Sintoma", "Tremor")
with col2:
    if st.button("🔴 EM OFF", use_container_width=True): registrar_clique("Estado", "Início OFF")
    if st.button("🔵 COMIDA", use_container_width=True): registrar_clique("Atividade", "Alimentação")
    if st.button("🧱 RIGIDEZ", use_container_width=True): registrar_clique("Sintoma", "Rigidez")

st.markdown("---")

# --- GRÁFICOS ---
if st.session_state['diario_v3']:
    df = pd.DataFrame(st.session_state['diario_v3'])
    
    tab_dia, tab_mes = st.tabs(["📅 Hoje", "📈 Mês"])
    
    with tab_dia:
        hoje = datetime.now().strftime("%d/%m/%Y")
        df_hoje = df[df['Data'] == hoje]
        if not df_hoje.empty:
            fig_dia = px.scatter(df_hoje, x="Categoria", y="Decimal", color="Categoria",
                                 text="Hora", title="Distribuição de Hoje")
            fig_dia.update_traces(marker=dict(size=30), textposition="top center")
            fig_dia.update_layout(yaxis=dict(range=[24, 0], dtick=1), showlegend=False)
            st.plotly_chart(fig_dia, use_container_width=True, config={'staticPlot': True})
        else:
            st.info("Aguardando registros de hoje.")

    with tab_mes:
        st.write("### Evolução Mensal")
        # Gráfico de barras acumulado
        fig_mes = px.bar(df, x="Data", y="Contagem", color="Categoria", title="Eventos por Dia")
        st.plotly_chart(fig_mes, use_container_width=True)
        
        if st.checkbox("Ver lista detalhada"):
            st.dataframe(df[["Data", "Hora", "Categoria", "Descricao"]], use_container_width=True)
else:
    st.info("Nada registrado. Os gráficos aparecerão após o primeiro clique.")
