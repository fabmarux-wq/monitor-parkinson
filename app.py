import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# 1. Configuração de tela
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# --- MEMÓRIA DO APP ---
if 'v14_dados' not in st.session_state: st.session_state['v14_dados'] = []
if 'off_inicio' not in st.session_state: st.session_state['off_inicio'] = None
if 'treino_inicio' not in st.session_state: st.session_state['treino_inicio'] = None
if 'menu' not in st.session_state: st.session_state['menu'] = None

# --- CORES DOS BOTÕES (Lógica de Alerta) ---
cor_off = "#FF0000" if st.session_state.off_inicio else "#F0F2F6"
cor_treino = "#FFD700" if st.session_state.treino_inicio else "#F0F2F6"
txt_off = "white" if st.session_state.off_inicio else "black"

st.markdown(f"""
<style>
    .stButton > button {{ 
        height: 100px !important; font-size: 22px !important; 
        font-weight: bold !important; border-radius: 25px; margin-bottom: 15px;
    }}
    /* Botão Finalizar OFF Ativo */
    button[key="f_off"] {{ background-color: {cor_off} !important; color: {txt_off} !important; }}
    /* Botão Finalizar Treino Ativo */
    button[key="f_tre"] {{ background-color: {cor_treino} !important; color: black !important; }}
</style>
""", unsafe_allow_html=True)

st.title("📊 Monitor Parkinson")

# Criando as Duas Abas
aba_registro, aba_grafico = st.tabs(["📝 REGISTRAR", "📈 VER GRÁFICOS"])

# --- ABA 1: ENTRADA DE DADOS ---
with aba_registro:
    st.subheader("Controle de Tempo (OFF e Treino)")
    
    # Linha do OFF
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔴 INICIAR\nOFF", key="i_off"):
            st.session_state.off_inicio = datetime.now().hour + datetime.now().minute/60
            st.rerun()
    with c2:
        label_off = "🏁 FINALIZAR\nOFF (ATIVO)" if st.session_state.off_inicio else "🏁 FINALIZAR\nOFF"
        if st.button(label_off, key="f_off"):
            if st.session_state.off_inicio:
                agora = datetime.now().hour + datetime.now().minute/60
                st.session_state['v14_dados'].append({
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Cat": "OFF", "Desc": "Período OFF", 
                    "Ini": st.session_state.off_inicio, "Fim": agora, "Qtd": 1
                })
                st.session_state.off_inicio = None
                st.rerun()

    # Linha do Treino
    c3, c4 = st.columns(2)
    with c3:
        if st.button("🏃 INICIAR\nTREINO", key="i_tre"):
            st.session_state.treino_inicio = datetime.now().hour + datetime.now().minute/60
            st.rerun()
    with c4:
        label_tre = "🏁 FINALIZAR\nTREINO (ATIVO)" if st.session_state.treino_inicio else "🏁 FINALIZAR\nTREINO"
        if st.button(label_tre, key="f_tre"):
            if st.session_state.treino_inicio:
                agora = datetime.now().hour + datetime.now().minute/60
                st.session_state['v14_dados'].append({
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Cat": "Treino", "Desc": "Exercício", 
                    "Ini": st.session_state.treino_inicio, "Fim": agora, "Qtd": 1
                })
                st.session_state.treino_inicio = None
                st.rerun()

    st.divider()
    st.subheader("Registros Rápidos")
    
    c5, c6 = st.columns(2)
    with c5:
        if st.button("🟢 REMÉDIOS", key="m_btn"): st.session_state.menu = "Med"
    with c6:
        if st.button("🔵 COMIDA", key="a_btn"): st.session_state.menu = "Ali"

    # Formulários Simples
    if st.session_state.menu == "Med":
        remedios = st.multiselect("Remédios tomados:", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
        if st.button("CONFIRMAR REMÉDIO"):
            h = datetime.now().hour + datetime.now().minute/60
            st.session_state['v14_dados'].append({
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Cat": "Medicação", "Desc": ", ".join(remedios), 
                "Ini": h, "Fim": h + 1.0, "Qtd": 1 # Bloco de 1 hora para aparecer bem
            })
            st.session_state.menu = None
            st.rerun()
    
    elif st.session_state.menu == "Ali":
        comida = st.text_input("O que comeu?")
        if st.button("CONFIRMAR COMIDA"):
            h = datetime.now().hour + datetime.now().minute/60
            st.session_state['v14_dados'].append({
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Cat": "Alimentação", "Desc": comida, 
                "Ini": h, "Fim": h + 1.0, "Qtd": 1 # Bloco de 1 hora
            })
            st.session_state.menu = None
            st.rerun()

# --- ABA 2: VISUALIZAÇÃO ---
with aba_grafico:
    if st.session_state['v14_dados']:
        df = pd.DataFrame(st.session_state['v14_dados'])
        hoje = datetime.now().strftime("%d/%m/%Y")
        df_h = df[df['Data'] == hoje]
        
        st.subheader(f"Hoje: {hoje}")
        
        # GRÁFICO DIÁRIO 0-24h
        fig = go.Figure()
        cores = {"Medicação": "#198754", "OFF": "#dc3545", "Treino": "#ffc107", "Alimentação": "#0dcaf0"}
        
        for _, r in df_h.iterrows():
            fig.add_trace(go.Scatter(
                x=[r['Cat'], r['Cat']], y=[r['Ini'], r['Fim']],
                mode='lines', line=dict(color=cores.get(r['Cat'], "#000"), width=50),
                name=r['Cat'], hoverinfo='text', text=f"{r['Desc']}"
            ))

        fig.update_layout(
            yaxis=dict(range=[0, 24], dtick=1, title="Horas do Dia (0=Base)"),
            xaxis=dict(title="Categorias"), height=700, showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        st.subheader("Resumo Mensal")
        fig_mes = px.bar(df, x="Data", y="Qtd", color="Cat", color_discrete_map=cores)
        st.plotly_chart(fig_mes, use_container_width=True)
        
        # Opção de baixar os dados
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Relatório", data=csv, file_name='monitor_parkinson.csv')
    else:
        st.info("Nada registrado ainda. Vá na aba 'REGISTRAR' para começar.")

# Reset na lateral
if st.sidebar.button("🗑️ LIMPAR TUDO"):
    st.session_state['v14_dados'] = []
    st.rerun()
