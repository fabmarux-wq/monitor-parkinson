import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Configuração para o Samsung A56
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# --- ESTADO DO APLICATIVO ---
if 'v9_dados' not in st.session_state: st.session_state['v9_dados'] = []
if 'off_inicio' not in st.session_state: st.session_state['off_inicio'] = None
if 'treino_inicio' not in st.session_state: st.session_state['treino_inicio'] = None
if 'menu' not in st.session_state: st.session_state['menu'] = None

# --- ESTILO DOS BOTÕES ---
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

# Função para salvar eventos
def salvar_evento(cat, desc, h_ini, h_fim=None):
    agora = datetime.now()
    st.session_state['v9_dados'].append({
        "Data": agora.strftime("%d/%m/%Y"),
        "Categoria": cat,
        "Descricao": desc,
        "Inicio": float(h_ini),
        "Fim": float(h_fim) if h_fim is not None else None,
        "Hora_Txt": agora.strftime("%H:%M")
    })

# --- BLOCO 1: ESTADO OFF ---
st.subheader("🔴 Controle de OFF (Barras)")
c1, c2 = st.columns(2)
with c1:
    if st.button("INICIAR\nOFF", key="btn_ini_off"):
        st.session_state.menu = "OFF"
with c2:
    if st.session_state.off_inicio is not None:
        st.markdown('<div class="btn-off-ativo">', unsafe_allow_html=True)
        if st.button("FINALIZAR\nOFF (ATIVO)", key="btn_fim_off"):
            agora = datetime.now()
            salvar_evento("OFF", "Duração OFF", st.session_state.off_inicio, agora.hour + agora.minute/60)
            st.session_state.off_inicio = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.button("FINALIZAR\nOFF", key="btn_fim_off_des", disabled=True)

# --- BLOCO 2: TREINO ---
st.subheader("🏃 Controle de Treino (Barras)")
c3, c4 = st.columns(2)
with c3:
    if st.button("INICIAR\nTREINO", key="btn_ini_tre"):
        agora = datetime.now()
        st.session_state.treino_inicio = agora.hour + agora.minute/60
        st.toast("Treino iniciado!")
        st.rerun()
with c4:
    if st.session_state.treino_inicio is not None:
        st.markdown('<div class="btn-treino-ativo">', unsafe_allow_html=True)
        if st.button("FINALIZAR\nTREINO (ATIVO)", key="btn_fim_tre"):
            agora = datetime.now()
            salvar_evento("Treino", "Duração Treino", st.session_state.treino_inicio, agora.hour + agora.minute/60)
            st.session_state.treino_inicio = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.button("FINALIZAR\nTREINO", key="btn_fim_tre_des", disabled=True)

st.divider()

# --- BLOCO 3: PONTUAIS (QUADRADOS) ---
c5, c6 = st.columns(2)
with c5:
    if st.button("🟢 REMÉDIOS", key="btn_med"): st.session_state.menu = "Med"
with c6:
    if st.button("🔵 COMIDA", key="btn_ali"): st.session_state.menu = "Ali"

# --- FORMULÁRIOS ---
if st.session_state.menu == "OFF":
    sints = st.multiselect("Sintomas iniciais:", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
    if st.button("COMEÇAR OFF AGORA"):
        agora = datetime.now()
        st.session_state.off_inicio = agora.hour + agora.minute/60
        st.session_state.menu = None
        st.rerun()

elif st.session_state.menu == "Med":
    remedios = st.multiselect("O que tomou?", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
    if st.button("SALVAR REMÉDIOS"):
        agora = datetime.now()
        salvar_evento("Medicação", ", ".join(remedios), agora.hour + agora.minute/60)
        st.session_state.menu = None
        st.rerun()

elif st.session_state.menu == "Ali":
    comida = st.text_input("O que comeu?")
    if st.button("SALVAR ALIMENTAÇÃO"):
        agora = datetime.now()
        salvar_evento("Alimentação", comida, agora.hour + agora.minute/60)
        st.session_state.menu = None
        st.rerun()

if st.session_state.menu:
    if st.button("Cancelar X"):
        st.session_state.menu = None
        st.rerun()

# --- GRÁFICO DIÁRIO (EIXO CRESCENTE 0-24) ---
st.divider()
st.write("### Gráfico de Atividades")

if st.session_state['v9_dados']:
    df = pd.DataFrame(st.session_state['v9_dados'])
    hoje = datetime.now().strftime("%d/%m/%Y")
    df_h = df[df['Data'] == hoje]
    
    fig = go.Figure()
    cores = {"Medicação": "#198754", "OFF": "#dc3545", "Treino": "#ffc107", "Alimentação": "#0dcaf0"}

    for _, r in df_h.iterrows():
        cor = cores.get(r['Categoria'], "#000")
        
        # Se for intervalo (OFF ou Treino), desenha uma BARRA (linha grossa)
        if r['Fim'] is not None:
            fig.add_trace(go.Scatter(
                x=[r['Categoria'], r['Categoria']],
                y=[r['Inicio'], r['Fim']],
                mode='lines',
                line=dict(color=cor, width=40),
                name=r['Categoria'],
                hoverinfo='text',
                text=f"{r['Categoria']}: {r['Inicio']:.2f} às {r['Fim']:.2f}"
            ))
        # Se for pontual (Medicação ou Alimentação), desenha um QUADRADO
        else:
            fig.add_trace(go.Scatter(
                x=[r['Categoria']],
                y=[r['Inicio']],
                mode='markers',
                marker=dict(symbol='square', size=25, color=cor),
                name=r['Categoria'],
                hoverinfo='text',
                text=f"{r['Categoria']}: {r['Descricao']}"
            ))

    # Configuração do Eixo Vertical: Começa em 0 (base) e vai até 24 (topo)
    fig.update_layout(
        yaxis=dict(
            range=[0, 24], 
            dtick=2, 
            title="Horas do Dia",
            autorange=False # Força o 0 ficar embaixo
        ),
        xaxis=dict(title="Categorias"),
        height=600,
        showlegend=False,
        dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

# Limpar memória
if st.sidebar.button("🗑️ LIMPAR TUDO"):
    st.session_state['v9_dados'] = []
    st.session_state.off_inicio = None
    st.session_state.treino_inicio = None
    st.rerun()
