import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração para celular
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# CSS para deixar os botões e textos grandes e amigáveis
st.markdown("""
<style>
    .stButton > button { height: 75px !important; font-size: 22px !important; font-weight: bold !important; border-radius: 20px; }
    .stTabs [data-baseweb="tab"] p { font-size: 24px !important; font-weight: bold !important; }
    label { font-size: 22px !important; font-weight: bold !important; }
    .stSelectbox div { font-size: 20px !important; }
</style>
""", unsafe_allow_stdio=True)

st.title("📊 Monitor Parkinson Pro")

if 'dados' not in st.session_state:
    st.session_state.dados = []
if 'menu' not in st.session_state:
    st.session_state.menu = None

# --- BOTÕES DE REGISTRO (COLORIDOS) ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🟢\nMED", use_container_width=True): st.session_state.menu = "Med"
with c2:
    if st.button("🔴\nOFF", use_container_width=True): st.session_state.menu = "OFF"
with c3:
    if st.button("🟡\nEXE", use_container_width=True): st.session_state.menu = "Exe"
with c4:
    if st.button("🔵\nALI", use_container_width=True): st.session_state.menu = "Ali"

st.markdown("---")

hoje_str = datetime.now().strftime("%Y-%m-%d")

# --- FORMULÁRIOS COM HORÁRIO DE 10 EM 10 MINUTOS ---
if st.session_state.menu:
    st.subheader(f"Registrando {st.session_state.menu}")
    
    # Voltando ao seletor único de tempo, mas com passo de 10 minutos (600 segundos)
    # Se o relógio do Android travar, o usuário pode digitar ou usar as setas
    h_escolha = st.time_input("Horário (ajuste de 10 em 10 min):", datetime.now().time(), step=600)
    h_dec = float(h_escolha.hour + h_escolha.minute/60)

    if st.session_state.menu == "Med":
        sel = st.multiselect("Remédios (marque vários):", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
        if st.button("SALVAR MEDICAÇÃO", use_container_width=True):
            for m in sel:
                n = m.split("(")[1].replace(")", "")
                st.session_state.dados.append({"Data": hoje_str, "H": h_dec, "Cat": "Med", "Txt": n, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "OFF":
        sints = st.multiselect("Sintomas (Tremor, Rigidez...):", ["Tremor", "Rigidez", "Lentidão", "Congelamento"])
        h_fim = st.time_input("Previsão de Término:", h_escolha, step=600)
        if st.button("SALVAR ESTADO OFF", use_container_width=True):
            t = ", ".join(sints) if sints else "OFF"
            st.session_state.dados.append({"Data": hoje_str, "H": h_dec, "H_Fim": float(h_fim.hour + h_fim.minute/60), "Cat": "OFF", "Txt": t, "Tipo": "Periodo"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Exe":
        txt_e = st.text_input("Atividade realizada:")
        if st.button("SALVAR EXERCÍCIO", use_container_width=True):
            st.session_state.dados.append({"Data": hoje_str, "H": h_dec, "Cat": "Exe", "Txt": txt_e, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    elif st.session_state.menu == "Ali":
        txt_a = st.text_input("O que comeu?")
        if st.button("SALVAR ALIMENTAÇÃO", use_container_width=True):
            st.session_state.dados.append({"Data": hoje_str, "H": h_dec, "Cat": "Ali", "Txt": txt_a, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.rerun()

    if st.button("Fechar formulário ❌"):
        st.session_state.menu = None
        st.rerun()

# --- GRÁFICO DIÁRIO FIXO E ABAS ---
tab_hoje, tab_historico = st.tabs(["📅 Hoje", "📈 Histórico"])

with tab_hoje:
    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)
        df_h = df[df['Data'] == hoje_str]
        
        if not df_h.empty:
            fig = go.Figure()
            cores = {"Med": "#198754", "OFF": "#dc3545", "Exe": "#ffc107", "Ali": "#0dcaf0"}
            for _, r in df_h.iterrows():
                c = cores.get(r['Cat'], "#000")
                if 'H_Fim' in r and not pd.isna(r['H_Fim']):
                    fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[float(r['H']), float(r['H_Fim'])], mode='lines', line=dict(color=c, width=40)))
                else:
                    fig.add_trace(go.Scatter(x=[r['Cat']], y=[float(r['H'])], mode='markers+text', marker=dict(symbol='square', size=20, color=c), text=[r['Txt']], textposition="middle right"))
            
            fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=600, showlegend=False, dragmode=False)
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
        else:
            st.info("Aguardando registros para hoje.")

with tab_historico:
    if st.session_state.dados:
        st.write("Registros salvos:")
        st.dataframe(pd.DataFrame(st.session_state.dados), use_container_width=True)

# Botão para zerar tudo (discreto na lateral)
if st.sidebar.button("Limpar Testes"):
    st.session_state.dados = []
    st.rerun()
