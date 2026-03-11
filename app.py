import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. Configuração para o Samsung A56
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# --- LÓGICA DE ESTADO (PARA AS CORES) ---
if 'v7_dados' not in st.session_state: st.session_state['v7_dados'] = []
if 'menu_aberto' not in st.session_state: st.session_state['menu_aberto'] = None
if 'off_ativo' not in st.session_state: st.session_state['off_ativo'] = False
if 'treino_ativo' not in st.session_state: st.session_state['treino_ativo'] = False

# 2. ESTILO CSS DINÂMICO
# Aqui controlamos as cores dos botões de finalizar com base no clique
cor_off = "#dc3545" if st.session_state.off_ativo else "#f0f2f6"
cor_treino = "#ffc107" if st.session_state.treino_ativo else "#f0f2f6"
texto_off = "white" if st.session_state.off_ativo else "black"
texto_treino = "black"

st.markdown(f"""
<style>
    /* Botões Gerais */
    .stButton > button {{ 
        height: 80px !important; font-size: 20px !important; 
        font-weight: bold !important; border-radius: 20px;
        margin-bottom: 10px;
    }}
    /* Cor do botão Finalizar OFF quando ativo */
    div[data-testid="column"]:nth-of-type(2) button:contains("FINALIZAR OFF") {{
        background-color: {cor_off} !important;
        color: {texto_off} !important;
    }}
    /* Cor do botão Finalizar Treino quando ativo */
    div[data-testid="column"]:nth-of-type(2) button:contains("FINALIZAR TREINO") {{
        background-color: {cor_treino} !important;
        color: {texto_treino} !important;
    }}
</style>
""", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson Pro")

# Função de salvamento (Hora Instantânea)
def salvar_clique(cat, nome):
    agora = datetime.now()
    registro = {{
        "Data": agora.strftime("%d/%m/%Y"),
        "Hora": agora.strftime("%H:%M"),
        "Decimal": float(agora.hour + agora.minute/60),
        "Categoria": str(cat),
        "Descricao": str(nome),
        "Contador": 1
    }}
    st.session_state['v7_dados'].append(registro)
    st.session_state['menu_aberto'] = None
    st.toast(f"✅ Registrado às {agora.strftime('%H:%M')}")
    st.rerun()

# --- BLOCO 1: ESTADO OFF ---
st.write("### Controle de OFF")
c1, c2 = st.columns(2)
with c1:
    if st.button("🔴 INICIAR OFF", use_container_width=True):
        st.session_state['menu_aberto'] = "OFF"
with c2:
    if st.button("🏁 FINALIZAR OFF", use_container_width=True):
        if st.session_state.off_ativo:
            st.session_state.off_ativo = False
            salvar_clique("Estado", "Fim do OFF")

# --- BLOCO 2: TREINO ---
st.write("### Controle de Treino")
c3, c4 = st.columns(2)
with c3:
    if st.button("🏃 INICIAR TREINO", use_container_width=True):
        st.session_state.treino_ativo = True
        salvar_clique("Exercício", "Início do Treino")
with c4:
    if st.button("🏁 FINALIZAR TREINO", use_container_width=True):
        if st.session_state.treino_ativo:
            st.session_state.treino_ativo = False
            salvar_clique("Exercício", "Fim do Treino")

st.markdown("---")

# --- OUTROS BOTÕES ---
c5, c6 = st.columns(2)
with c5:
    if st.button("🟢 MEDICAMENTOS", use_container_width=True): st.session_state['menu_aberto'] = "Med"
with c6:
    if st.button("🔵 COMIDA", use_container_width=True): st.session_state['menu_aberto'] = "Ali"

# --- FORMULÁRIOS QUE ABREM AO CLICAR ---
if st.session_state['menu_aberto'] == "OFF":
    st.subheader("⚠️ Sintomas Iniciais")
    sints = st.multiselect("Marque os sintomas:", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
    if st.button("SALVAR E COMEÇAR OFF"):
        st.session_state.off_ativo = True
        txt = "Início OFF: " + ", ".join(sints)
        salvar_clique("Estado", txt)

elif st.session_state['menu_aberto'] == "Med":
    st.subheader("💊 Medicamentos")
    escolhidos = st.multiselect("O que tomou agora?", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
    if st.button("SALVAR REMÉDIOS"):
        salvar_clique("Medicação", ", ".join(escolhidos))

elif st.session_state['menu_aberto'] == "Ali":
    st.subheader("🍽️ Alimentação")
    o_que = st.text_input("O que comeu?")
    if st.button("SALVAR ALIMENTAÇÃO"):
        salvar_clique("Alimentação", o_que)

# --- GRÁFICOS ---
if st.session_state['v7_dados']:
    st.divider()
    df = pd.DataFrame(st.session_state['v7_dados'])
    tab1, tab2 = st.tabs(["📅 Gráfico de Hoje", "📈 Histórico Mensal"])
    
    with tab1:
        hoje = datetime.now().strftime("%d/%m/%Y")
        df_hoje = df[df['Data'] == hoje]
        if not df_hoje.empty:
            fig_dia = px.scatter(df_hoje, x="Categoria", y="Decimal", color="Categoria",
                                 text="Hora", title="Suas Atividades")
            fig_dia.update_traces(marker=dict(size=25), textposition="top center")
            fig_dia.update_layout(yaxis=dict(range=[24, 0], dtick=1), showlegend=False)
            st.plotly_chart(fig_dia, use_container_width=True, config={'staticPlot': True})

    with tab2:
        fig_mes = px.bar(df, x="Data", y="Contador", color="Categoria", title="Frequência Mensal")
        st.plotly_chart(fig_mes, use_container_width=True)
        if st.checkbox("Ver lista de registros"):
            st.dataframe(df[["Data", "Hora", "Categoria", "Descricao"]], use_container_width=True)

# Reset na lateral
if st.sidebar.button("🗑️ LIMPAR TUDO"):
    st.session_state['v7_dados'] = []
    st.session_state.off_ativo = False
    st.session_state.treino_ativo = False
    st.rerun()
