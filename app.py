import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Configuração para o Samsung A56
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# --- MEMÓRIA DO APLICATIVO ---
if 'v11_dados' not in st.session_state: st.session_state['v11_dados'] = []
if 'off_inicio' not in st.session_state: st.session_state['off_inicio'] = None
if 'treino_inicio' not in st.session_state: st.session_state['treino_inicio'] = None
if 'menu' not in st.session_state: st.session_state['menu'] = None

# --- ESTILO DOS BOTÕES ---
st.markdown("""
<style>
    .stButton > button { 
        height: 90px !important; font-size: 22px !important; 
        font-weight: bold !important; border-radius: 25px;
        margin-bottom: 10px; width: 100%;
    }
    .btn-off-ativo button { background-color: #ff4b4b !important; color: white !important; border: 3px solid black !important; }
    .btn-treino-ativo button { background-color: #ffeb3b !important; color: black !important; border: 3px solid black !important; }
    .stTabs [data-baseweb="tab"] p { font-size: 20px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson Pro")

# Função para salvar eventos
def salvar_evento(cat, desc, h_ini, h_fim=None):
    agora = datetime.now()
    st.session_state['v11_dados'].append({
        "Data": agora.strftime("%d/%m/%Y"),
        "Categoria": cat,
        "Descricao": desc,
        "Inicio": float(h_ini),
        "Fim": float(h_fim) if h_fim is not None else None,
        "Qtd": 1
    })

# --- BLOCOS DE CONTROLE (INÍCIO E FIM) ---
st.subheader("🔴 Controle de OFF")
c1, c2 = st.columns(2)
with c1:
    if st.button("INICIAR\nOFF", key="off_start"):
        agora = datetime.now()
        st.session_state.off_inicio = agora.hour + agora.minute/60
        st.rerun()
with c2:
    if st.session_state.off_inicio is not None:
        st.markdown('<div class="btn-off-ativo">', unsafe_allow_html=True)
        if st.button("FINALIZAR\nOFF (ATIVO)", key="off_end"):
            agora = datetime.now()
            salvar_evento("OFF", "Duração OFF", st.session_state.off_inicio, agora.hour + agora.minute/60)
            st.session_state.off_inicio = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.button("FINALIZAR\nOFF", disabled=True, key="off_end_off")

st.subheader("🏃 Controle de Treino")
c3, c4 = st.columns(2)
with c3:
    if st.button("INICIAR\nTREINO", key="treino_start"):
        agora = datetime.now()
        st.session_state.treino_inicio = agora.hour + agora.minute/60
        st.rerun()
with c4:
    if st.session_state.treino_inicio is not None:
        st.markdown('<div class="btn-treino-ativo">', unsafe_allow_html=True)
        if st.button("FINALIZAR\nTREINO (ATIVO)", key="treino_end"):
            agora = datetime.now()
            salvar_evento("Treino", "Duração Treino", st.session_state.treino_inicio, agora.hour + agora.minute/60)
            st.session_state.treino_inicio = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.button("FINALIZAR\nTREINO", disabled=True, key="treino_end_off")

st.divider()

# --- REGISTROS PONTUAIS ---
c5, c6 = st.columns(2)
with c5:
    if st.button("🟢 REMÉDIOS"): st.session_state.menu = "Med"
with c6:
    if st.button("🔵 COMIDA"): st.session_state.menu = "Ali"

if st.session_state.menu == "Med":
    remedios = st.multiselect("O que tomou?", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
    if st.button("SALVAR AGORA"):
        agora = datetime.now()
        salvar_evento("Medicação", ", ".join(remedios), agora.hour + agora.minute/60)
        st.session_state.menu = None
        st.rerun()
elif st.session_state.menu == "Ali":
    comida = st.text_input("O que comeu?")
    if st.button("SALVAR COMIDA"):
        agora = datetime.now()
        salvar_evento("Alimentação", comida, agora.hour + agora.minute/60)
        st.session_state.menu = None
        st.rerun()
if st.session_state.menu and st.button("Fechar X"):
    st.session_state.menu = None
    st.rerun()

# --- GRÁFICOS (DIÁRIO E MENSAL) ---
st.divider()
if st.session_state['v11_dados']:
    df = pd.DataFrame(st.session_state['v11_dados'])
    tab1, tab2 = st.tabs(["📅 Gráfico de Hoje", "📈 Evolução Mensal"])
    
    with tab1:
        hoje = datetime.now().strftime("%d/%m/%Y")
        df_h = df[df['Data'] == hoje]
        
        fig = go.Figure()
        cores = {"Medicação": "#198754", "OFF": "#dc3545", "Treino": "#ffc107", "Alimentação": "#0dcaf0"}

        if not df_h.empty:
            for _, r in df_h.iterrows():
                cor = cores.get(r['Categoria'], "#000")
                if r['Fim'] is not None:
                    fig.add_trace(go.Scatter(x=[r['Categoria'], r['Categoria']], y=[r['Inicio'], r['Fim']],
                                         mode='lines', line=dict(color=cor, width=45), name=r['Categoria']))
                else:
                    fig.add_trace(go.Scatter(x=[r['Categoria']], y=[r['Inicio']],
                                         mode='markers', marker=
