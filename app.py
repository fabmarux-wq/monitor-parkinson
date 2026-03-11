import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# 1. Configuração para o Samsung A56
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# --- MEMÓRIA DO APP ---
if 'v15_dados' not in st.session_state: st.session_state['v15_dados'] = []
if 'off_inicio' not in st.session_state: st.session_state['off_inicio'] = None
if 'treino_inicio' not in st.session_state: st.session_state['treino_inicio'] = None
if 'menu' not in st.session_state: st.session_state['menu'] = None

# --- ESTILO DOS BOTÕES (Cores Fixas) ---
cor_off = "#FF0000" if st.session_state.off_inicio else "#F0F2F6"
cor_treino = "#FFD700" if st.session_state.treino_inicio else "#F0F2F6"
txt_off = "white" if st.session_state.off_inicio else "black"

st.markdown(f"""
<style>
    .stButton > button {{ 
        height: 95px !important; font-size: 22px !important; 
        font-weight: bold !important; border-radius: 25px; margin-bottom: 12px;
    }}
    /* Cores forçadas para os botões de finalizar */
    button[key="f_off"] {{ background-color: {cor_off} !important; color: {txt_off} !important; border: 3px solid black !important; }}
    button[key="f_tre"] {{ background-color: {cor_treino} !important; color: black !important; border: 3px solid black !important; }}
</style>
""", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson")

# --- ABAS ---
aba_reg, aba_graf = st.tabs(["📝 REGISTRAR", "📈 VER GRÁFICOS"])

with aba_reg:
    st.subheader("OFF e Treino")
    # OFF
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔴 INICIAR\nOFF", key="i_off"):
            st.session_state.off_inicio = datetime.now().hour + datetime.now().minute/60
            st.rerun()
    with c2:
        if st.button("🏁 FINALIZAR\nOFF", key="f_off"):
            if st.session_state.off_inicio:
                agora = datetime.now().hour + datetime.now().minute/60
                st.session_state['v15_dados'].append({
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Dia_Mes": datetime.now().strftime("%d"),
                    "Cat": "OFF", "Ini": st.session_state.off_inicio, "Fim": agora
                })
                st.session_state.off_inicio = None
                st.rerun()

    # Treino
    c3, c4 = st.columns(2)
    with c3:
        if st.button("🏃 INICIAR\nTREINO", key="i_tre"):
            st.session_state.treino_inicio = datetime.now().hour + datetime.now().minute/60
            st.rerun()
    with c4:
        if st.button("🏁 FINALIZAR\nTREINO", key="f_tre"):
            if st.session_state.treino_inicio:
                agora = datetime.now().hour + datetime.now().minute/60
                st.session_state['v15_dados'].append({
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Dia_Mes": datetime.now().strftime("%d"),
                    "Cat": "Treino", "Ini": st.session_state.treino_inicio, "Fim": agora
                })
                st.session_state.treino_inicio = None
                st.rerun()

    st.divider()
    # Medicamento e Comida
    c5, c6 = st.columns(2)
    with c5:
        if st.button("🟢 REMÉDIOS"): st.session_state.menu = "Med"
    with c6:
        if st.button("🔵 COMIDA"): st.session_state.menu = "Ali"

    if st.session_state.menu == "Med":
        remedios = st.multiselect("Remédios:", ["Prolopa BD", "Mantidan", "Pramipexol", "Rasagilina", "Prolopa HBS", "Prolopa D"])
        if st.button("SALVAR REMÉDIO"):
            h = datetime.now().hour + datetime.now().minute/60
            st.session_state['v15_dados'].append({
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Dia_Mes": datetime.now().strftime("%d"),
                "Cat": "Medicação", "Ini": h, "Fim": h + 1.0 # Bloco de 1h
            })
            st.session_state.menu = None
            st.rerun()
    elif st.session_state.menu == "Ali":
        comida = st.text_input("O que comeu?")
        if st.button("SALVAR COMIDA"):
            h = datetime.now().hour + datetime.now().minute/60
            st.session_state['v15_dados'].append({
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Dia_Mes": datetime.now().strftime("%d"),
                "Cat": "Alimentação", "Ini": h, "Fim": h + 1.0 # Bloco de 1h
            })
            st.session_state.menu = None
            st.rerun()

# --- ABA DE GRÁFICOS ---
with aba_graf:
    if st.session_state['v15_dados']:
        df = pd.DataFrame(st.session_state['v15_dados'])
        hoje = datetime.now().strftime("%d/%m/%Y")
        cores = {"Medicação": "#198754", "OFF": "#dc3545", "Treino": "#ffc107", "Alimentação": "#0dcaf0"}

        # --- 1. GRÁFICO DIÁRIO (Categorias x Horas) ---
        st.subheader(f"Diário: {hoje}")
        df_h = df[df['Data'] == hoje]
        fig_dia = go.Figure()
        for _, r in df_h.iterrows():
            fig_dia.add_trace(go.Scatter(
                x=[r['Cat'], r['Cat']], y=[r['Ini'], r['Fim']],
                mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=50)
            ))
        fig_dia.update_layout(yaxis=dict(range=[0, 24], dtick=1, title="Horas"), 
                             xaxis=dict(title="Atividade"), height=500, showlegend=False)
        # CONFIGURAÇÃO ESTÁTICA (Trava o toque/zoom)
        st.plotly_chart(fig_dia, use_container_width=True, config={'staticPlot': True})

        st.divider()

        # --- 2. GRÁFICO MENSAL (Dias x Horas) ---
        st.subheader("Mapa do Mês")
        fig_mes = go.Figure()
        for _, r in df.iterrows():
            fig_mes.add_trace(go.Scatter(
                x=[r['Data'], r['Data']], y=[r['Ini'], r['Fim']],
                mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=20)
            ))
        # Y vai de 0 a 24, X são os dias do mês
        fig_mes.update_layout(yaxis=dict(range=[0, 24], dtick=1, title="Horas do Dia"),
                             xaxis=dict(title="Dias do Mês", type='category'), 
                             height=600, showlegend=False)
        st.plotly_chart(fig_mes, use_container_width=True, config={'staticPlot': True})
        
        # Botão para baixar
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha", data=csv, file_name='parkinson.csv')

    else:
        st.info("Registre algo para ver os gráficos.")

# Reset lateral
if st.sidebar.button("🗑️ LIMPAR TUDO"):
    st.session_state['v15_dados'] = []
    st.rerun()
