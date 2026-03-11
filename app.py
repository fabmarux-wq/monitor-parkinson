import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuração para o Samsung A56
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# Estilo: Botões GIGANTES e fáceis de tocar
st.markdown("""
<style>
    .stButton > button { 
        height: 85px !important; 
        font-size: 22px !important; 
        font-weight: bold !important; 
        border-radius: 20px;
        margin-bottom: 12px;
    }
    .stTabs [data-baseweb="tab"] p { font-size: 22px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

st.title("⏱️ Registro Instantâneo")

# Memória v6
if 'v6_dados' not in st.session_state:
    st.session_state['v6_dados'] = []
if 'menu_aberto' not in st.session_state:
    st.session_state['menu_aberto'] = None

# Função de salvamento (Pega a hora do clique oficial)
def salvar_clique(cat, nome):
    agora = datetime.now()
    registro = {
        "Data": agora.strftime("%d/%m/%Y"),
        "Hora": agora.strftime("%H:%M"),
        "Decimal": float(agora.hour + agora.minute/60),
        "Categoria": str(cat),
        "Descricao": str(nome),
        "Contador": 1
    }
    st.session_state['v6_dados'].append(registro)
    st.session_state['menu_aberto'] = None
    st.toast(f"✅ {nome} salvo às {agora.strftime('%H:%M')}")
    st.rerun()

# --- BOTÕES DE ATALHO (INÍCIO E FIM) ---
st.write("### Controles de Início e Fim:")
c1, c2 = st.columns(2)
with c1:
    if st.button("🔴 INICIAR OFF", use_container_width=True): st.session_state['menu_aberto'] = "OFF"
    if st.button("🏃 INICIAR TREINO", use_container_width=True): salvar_clique("Exercício", "Início Treino")

with c2:
    if st.button("⚪ FINALIZAR OFF", use_container_width=True): salvar_clique("Estado", "Fim OFF")
    if st.button("🏁 FINALIZAR TREINO", use_container_width=True): salvar_clique("Exercício", "Fim Treino")

st.markdown("---")
st.write("### Outros Registros:")
if st.button("🟢 MEDICAMENTOS", use_container_width=True): st.session_state['menu_aberto'] = "Med"
if st.button("🔵 REGISTRAR COMIDA", use_container_width=True): st.session_state['menu_aberto'] = "Ali"

st.markdown("---")

# --- FORMULÁRIOS DINÂMICOS ---
if st.session_state['menu_aberto'] == "OFF":
    st.subheader("⚠️ Sintomas do OFF")
    sints = st.multiselect("Marque os sintomas de agora:", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
    if st.button("SALVAR INÍCIO DO OFF AGORA"):
        if sints:
            txt = "Início OFF: " + ", ".join(sints)
            salvar_clique("Estado", txt)

elif st.session_state['menu_aberto'] == "Med":
    st.subheader("💊 Selecione os Medicamentos")
    escolhidos = st.multiselect("Marque os remédios tomados agora:", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
    if st.button("SALVAR MEDICAMENTOS AGORA"):
        if escolhidos:
            txt = ", ".join(escolhidos)
            salvar_clique("Medicação", txt)

elif st.session_state['menu_aberto'] == "Ali":
    st.subheader("🍽️ O que você comeu?")
    o_que = st.text_input("Descreva brevemente:")
    if st.button("SALVAR COMIDA AGORA"):
        if o_que:
            salvar_clique("Alimentação", o_que)

if st.session_state['menu_aberto']:
    if st.button("Cancelar Registro X"):
        st.session_state['menu_aberto'] = None
        st.rerun()

# --- GRÁFICOS ---
if st.session_state['v6_dados']:
    st.markdown("---")
    df = pd.DataFrame(st.session_state['v6_dados'])
    
    tab_dia, tab_mes = st.tabs(["📅 Hoje", "📈 Mês"])
    
    with tab_dia:
        hoje = datetime.now().strftime("%d/%m/%Y")
        df_hoje = df[df['Data'] == hoje]
        if not df_hoje.empty:
            fig_dia = px.scatter(df_hoje, x="Categoria", y="Decimal", color="Categoria",
                                 text="Hora", title="Atividades de Hoje")
            fig_dia.update_traces(marker=dict(size=25), textposition="top center")
            fig_dia.update_layout(yaxis=dict(range=[24, 0], dtick=1), showlegend=False)
            st.plotly_chart(fig_dia, use_container_width=True, config={'staticPlot': True})
        else:
            st.write("Sem registros para hoje.")

    with tab_mes:
        st.write("### Frequência Mensal")
        fig_mes = px.bar(df, x="Data", y="Contador", color="Categoria", title="Eventos por Dia")
        st.plotly_chart(fig_mes, use_container_width=True)
        if st.checkbox("Ver tabela completa"):
            st.dataframe(df[["Data", "Hora", "Categoria", "Descricao"]], use_container_width=True)

# Botão de Reset
if st.sidebar.button("🗑️ LIMPAR TUDO"):
    st.session_state['v6_dados'] = []
    st.rerun()
