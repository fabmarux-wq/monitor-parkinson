import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Configuração para o Samsung A56
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# --- ESTADO DO APLICATIVO ---
if 'v8_dados' not in st.session_state: st.session_state['v8_dados'] = []
if 'off_ativo' not in st.session_state: st.session_state['off_ativo'] = False
if 'treino_ativo' not in st.session_state: st.session_state['treino_ativo'] = False
if 'menu' not in st.session_state: st.session_state['menu'] = None

# --- ESTILO DOS BOTÕES (SIMPLIFICADO PARA NÃO DAR ERRO) ---
st.markdown("""
<style>
    .stButton > button { 
        height: 90px !important; font-size: 22px !important; 
        font-weight: bold !important; border-radius: 20px;
        margin-bottom: 10px; width: 100%;
    }
    .btn-off-ativo button { background-color: #ff4b4b !important; color: white !important; border: 3px solid black !important; }
    .btn-treino-ativo button { background-color: #ffeb3b !important; color: black !important; border: 3px solid black !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson Pro")

# Função para salvar na hora exata
def salvar(cat, acao):
    agora = datetime.now()
    st.session_state['v8_dados'].append({
        "Data": agora.strftime("%d/%m/%Y"),
        "Hora": agora.strftime("%H:%M"),
        "Decimal": float(agora.hour + agora.minute/60),
        "Categoria": str(cat),
        "Descricao": str(acao),
        "Qtd": 1
    })
    st.toast(f"✅ {acao} salvo!")

# --- BLOCO 1: ESTADO OFF ---
st.subheader("🔴 Controle de OFF")
c1, c2 = st.columns(2)
with c1:
    if st.button("INICIAR\nOFF", key="iniciar_off"):
        st.session_state.menu = "OFF"
with c2:
    # Se o OFF estiver ativo, aplica a classe de cor vermelha
    container_off = st.container()
    if st.session_state.off_ativo:
        with container_off:
            st.markdown('<div class="btn-off-ativo">', unsafe_allow_html=True)
            if st.button("FINALIZAR\nOFF (ATIVO)", key="fim_off"):
                st.session_state.off_ativo = False
                salvar("Estado", "Fim do OFF")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        if st.button("FINALIZAR\nOFF", key="fim_off_off"):
            st.warning("O OFF não foi iniciado.")

# --- BLOCO 2: TREINO ---
st.subheader("🏃 Controle de Treino")
c3, c4 = st.columns(2)
with c3:
    if st.button("INICIAR\nTREINO", key="ini_tre"):
        st.session_state.treino_ativo = True
        salvar("Exercício", "Início Treino")
        st.rerun()
with c4:
    # Se o Treino estiver ativo, aplica a cor amarela
    container_treino = st.container()
    if st.session_state.treino_ativo:
        with container_treino:
            st.markdown('<div class="btn-treino-ativo">', unsafe_allow_html=True)
            if st.button("FINALIZAR\nTREINO (ATIVO)", key="fim_tre"):
                st.session_state.treino_ativo = False
                salvar("Exercício", "Fim Treino")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        if st.button("FINALIZAR\nTREINO", key="fim_tre_off"):
            st.warning("O Treino não foi iniciado.")

st.divider()

# --- OUTROS BOTÕES ---
c5, c6 = st.columns(2)
with c5:
    if st.button("🟢 REMÉDIOS", use_container_width=True): st.session_state.menu = "Med"
with c6:
    if st.button("🔵 COMIDA", use_container_width=True): st.session_state.menu = "Ali"

# --- FORMULÁRIOS ---
if st.session_state.menu == "OFF":
    st.write("### O que está sentindo?")
    sints = st.multiselect("Sintomas:", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
    if st.button("SALVAR E INICIAR OFF"):
        st.session_state.off_ativo = True
        st.session_state.menu = None
        salvar("Estado", "Início OFF: " + ", ".join(sints))
        st.rerun()

elif st.session_state.menu == "Med":
    st.write("### O que tomou agora?")
    remedios = st.multiselect("Medicamentos:", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
    if st.button("SALVAR REMÉDIOS"):
        st.session_state.menu = None
        salvar("Medicação", ", ".join(remedios))
        st.rerun()

elif st.session_state.menu == "Ali":
    st.write("### O que comeu?")
    comida = st.text_input("Descrição:")
    if st.button("SALVAR ALIMENTAÇÃO"):
        st.session_state.menu = None
        salvar("Alimentação", comida)
        st.rerun()

if st.session_state.menu:
    if st.button("Cancelar X"):
        st.session_state.menu = None
        st.rerun()

# --- GRÁFICOS ---
if st.session_state['v8_dados']:
    st.divider()
    df = pd.DataFrame(st.session_state['v8_dados'])
    t1, t2 = st.tabs(["📅 Hoje", "📈 Mês"])
    
    with t1:
        hoje = datetime.now().strftime("%d/%m/%Y")
        df_h = df[df['Data'] == hoje]
        if not df_h.empty:
            fig_dia = px.scatter(df_h, x="Categoria", y="Decimal", color="Categoria",
                                 text="Hora", title="Atividades de Hoje")
            fig_dia.update_traces(marker=dict(size=25), textposition="top center")
            fig_dia.update_layout(yaxis=dict(range=[24, 0], dtick=1), showlegend=False)
            st.plotly_chart(fig_dia, use_container_width=True, config={'staticPlot': True})

    with t2:
        st.write("### Evolução Mensal")
        fig_mes = px.bar(df, x="Data", y="Qtd", color="Categoria", title="Eventos por Dia")
        st.plotly_chart(fig_mes, use_container_width=True)
        if st.checkbox("Ver lista completa"):
            st.dataframe(df[["Data", "Hora", "Categoria", "Descricao"]], use_container_width=True)

# Limpar tudo na lateral
if st.sidebar.button("🗑️ LIMPAR TUDO"):
    st.session_state['v8_dados'] = []
    st.session_state.off_ativo = False
    st.session_state.treino_ativo = False
    st.rerun()
