import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuração focada em acessibilidade
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# Estilo: Botões GIGANTES e sem menus complicados
st.markdown("""
<style>
    .stButton > button { 
        height: 100px !important; 
        font-size: 26px !important; 
        font-weight: bold !important; 
        border-radius: 25px;
        margin-bottom: 12px;
    }
    .stTabs [data-baseweb="tab"] p { font-size: 24px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_stdio=True)

st.title("⏱️ Registro Instantâneo")

# Inicializa memória segura
if 'dados' not in st.session_state:
    st.session_state.dados = []

# FUNÇÃO INSTANTÂNEA: Clicou, salvou a hora oficial do sistema
def registrar_agora(categoria, texto):
    agora = datetime.now()
    # Guardamos os dados de forma simples para evitar erros de tipo
    novo = {
        "Data": agora.strftime("%Y-%m-%d"),
        "Hora": agora.strftime("%H:%M"),
        "H_Decimal": float(agora.hour + agora.minute/60),
        "Categoria": str(categoria),
        "Descricao": str(texto),
        "Contagem": 1
    }
    st.session_state.dados.append(novo)
    st.toast(f"✅ Registrado: {texto} às {novo['Hora']}")

# --- BOTÕES DE UM CLIQUE ---
st.write("### Toque para salvar agora:")
col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 PROLOPA", use_container_width=True): registrar_agora("Medicação", "Prolopa")
    if st.button("🟡 TREINO", use_container_width=True): registrar_agora("Exercício", "Treino")
    if st.button("🫨 TREMOR", use_container_width=True): registrar_agora("Sintoma", "Tremor")

with col2:
    if st.button("🔴 OFF", use_container_width=True): registrar_agora("Estado", "Início OFF")
    if st.button("🔵 COMIDA", use_container_width=True): registrar_agora("Alimentação", "Comida")
    if st.button("🧱 RIGIDEZ", use_container_width=True): registrar_agora("Sintoma", "Rigidez")

st.markdown("---")

# --- ABAS DE GRÁFICOS ---
tab_dia, tab_mes = st.tabs(["📅 Gráfico do Dia", "📈 Evolução Mensal"])

if st.session_state.dados:
    df = pd.DataFrame(st.session_state.dados)
    
    with tab_dia:
        hoje = datetime.now().strftime("%Y-%m-%d")
        df_hoje = df[df['Data'] == hoje]
        
        if not df_hoje.empty:
            fig_dia = go.Figure()
            cores = {"Medicação": "#198754", "Estado": "#dc3545", "Exercício": "#ffc107", "Alimentação": "#0dcaf0", "Sintoma": "#6f42c1"}
            
            for _, r in df_hoje.iterrows():
                fig_dia.add_trace(go.Scatter(
                    x=[r['Categoria']], y=[r['H_Decimal']],
                    mode='markers+text',
                    marker=dict(size=30, color=cores.get(r['Categoria'], "#000")),
                    text=[f"{r['Hora']} - {r['Descricao']}"],
                    textposition="middle right"
                ))
            fig_dia.update_layout(yaxis=dict(range=[24, 0], title="Hora do Dia"), height=500, showlegend=False)
            st.plotly_chart(fig_dia, use_container_width=True, config={'staticPlot': True})
        else:
            st.info("Nenhum registro hoje.")

    with tab_mes:
        st.write("### Frequência por dia:")
        # Gráfico de barras mostrando quantos registros por dia
        fig_mes = px.bar(df, x="Data", y="Contagem", color="Categoria", 
                         title="Atividades ao longo do mês",
                         color_discrete_map={"Medicação": "#198754", "Estado": "#dc3545", "Exercício": "#ffc107", "Alimentação": "#0dcaf0", "Sintoma": "#6f42c1"})
        st.plotly_chart(fig_mes, use_container_width=True)
        
        # Tabela detalhada
        if st.checkbox("Ver lista detalhada"):
            st.dataframe(df[["Data", "Hora", "Categoria", "Descricao"]], use_container_width=True)

else:
    st.info("Aguardando o primeiro registro para gerar os gráficos.")

# Botão de Reset localizado na lateral
if st.sidebar.button("🗑️ LIMPAR TUDO"):
    st.session_state.dados = []
    st.rerun()
