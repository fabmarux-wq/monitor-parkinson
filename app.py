import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração de tela
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# 2. Estilo dos botões (Corrigido para não dar TypeError)
st.markdown("""
<style>
    .stButton > button { 
        height: 100px !important; 
        font-size: 24px !important; 
        font-weight: bold !important; 
        border-radius: 20px;
        margin-bottom: 10px;
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

st.title("⏱️ Registro Instantâneo")

# 3. Memória limpa (v4 para evitar conflitos antigos)
if 'v4_dados' not in st.session_state:
    st.session_state['v4_dados'] = []

# Função para salvar no clique
def salvar_agora(cat, nome):
    agora = datetime.now()
    registro = {
        "Data": agora.strftime("%d/%m/%Y"),
        "Hora": agora.strftime("%H:%M"),
        "Decimal": float(agora.hour + agora.minute/60),
        "Categoria": str(cat),
        "Acao": str(nome),
        "Contador": 1
    }
    st.session_state['v4_dados'].append(registro)
    st.toast(f"✅ {nome} registrado!")

# --- BOTÃO DE RESET (LIMPEZA TOTAL) ---
if st.button("🛑 CLIQUE AQUI PARA DESTRAVAR O APP", use_container_width=True):
    st.session_state['v4_dados'] = []
    st.rerun()

st.markdown("---")

# --- BOTÕES DE UM CLIQUE ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 PROLOPA", use_container_width=True): salvar_agora("Remédio", "Prolopa")
    if st.button("🟡 TREINO", use_container_width=True): salvar_agora("Atividade", "Exercício")
    if st.button("🫨 TREMOR", use_container_width=True): salvar_agora("Sintoma", "Tremor")

with col2:
    if st.button("🔴 EM OFF", use_container_width=True): salvar_agora("Estado", "Início OFF")
    if st.button("🔵 COMIDA", use_container_width=True): salvar_agora("Atividade", "Alimentação")
    if st.button("🧱 RIGIDEZ", use_container_width=True): salvar_agora("Sintoma", "Rigidez")

st.markdown("---")

# --- GRÁFICOS ---
if st.session_state['v4_dados']:
    df = pd.DataFrame(st.session_state['v4_dados'])
    
    tab1, tab2 = st.tabs(["📅 Gráfico de Hoje", "📈 Gráfico do Mês"])
    
    with tab1:
        hoje = datetime.now().strftime("%d/%m/%Y")
        df_hoje = df[df['Data'] == hoje]
        if not df_hoje.empty:
            fig_dia = px.scatter(df_hoje, x="Categoria", y="Decimal", color="Categoria",
                                 text="Hora", title="Registros de Hoje")
            fig_dia.update_traces(marker=dict(size=25))
            fig_dia.update_layout(yaxis=dict(range=[24, 0], dtick=1), showlegend=False)
            st.plotly_chart(fig_dia, use_container_width=True, config={'staticPlot': True})
        else:
            st.write("Aguardando registros para hoje.")

    with tab2:
        st.write("### Frequência Mensal")
        fig_mes = px.bar(df, x="Data", y="Contador", color="Categoria", title="Eventos por Dia")
        st.plotly_chart(fig_mes, use_container_width=True)
        
        if st.checkbox("Ver tabela detalhada"):
            st.dataframe(df[["Data", "Hora", "Categoria", "Acao"]], use_container_width=True)
else:
    st.info("O diário está vazio. Toque nos botões para começar.")
