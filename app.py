import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configuração para celular
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

st.markdown("### Monitor Parkinson Pro")

# Inicializa a memória
if 'dados' not in st.session_state:
    st.session_state.dados = []
if 'menu' not in st.session_state:
    st.session_state.menu = None

# --- BOTÕES GRANDES E COLORIDOS (VERSÃO SEGURA) ---
# Usamos colunas para os botões ficarem lado a lado
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("🟢\nMed"): st.session_state.menu = "Med"
with c2:
    if st.button("🔴\nOFF"): st.session_state.menu = "OFF"
with c3:
    if st.button("🟡\nExe"): st.session_state.menu = "Exe"
with c4:
    if st.button("🔵\nAli"): st.session_state.menu = "Ali"

st.markdown("---")

# --- FORMULÁRIOS DE REGISTRO ---
if st.session_state.menu == "Med":
    st.subheader("💊 Medicação")
    h_m = st.time_input("Hora:", datetime.now().time())
    # Múltipla escolha ATIVADA
    sel = st.multiselect("Remédios:", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
    if st.button("SALVAR REMÉDIO"):
        for m in sel:
            n = m.split("(")[1].replace(")", "")
            st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_m.hour + (h_m.minute/60), "Cat": "Med", "Txt": n, "Tipo": "Ponto"})
        st.success("Salvo!")
        st.session_state.menu = None

elif st.session_state.menu == "OFF":
    st.subheader("⚠️ Estado OFF")
    h_i = st.time_input("Início:", time(8, 0))
    h_f = st.time_input("Fim:", time(9, 0))
    if st.button("SALVAR OFF"):
        st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_i.hour + (h_i.minute/60), "H_Fim": h_f.hour + (h_f.minute/60), "Cat": "OFF", "Txt": "!", "Tipo": "Periodo"})
        st.success("Salvo!")
        st.session_state.menu = None

elif st.session_state.menu == "Exe":
    st.subheader("🏃 Exercício")
    h_e = st.time_input("Hora:", datetime.now().time())
    txt_e = st.text_input("O que fez?")
    if st.button("SALVAR TREINO"):
        st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_e.hour + (h_e.minute/60), "Cat": "Exe", "Txt": txt_e, "Tipo": "Ponto"})
        st.success("Salvo!")
        st.session_state.menu = None

elif st.session_state.menu == "Ali":
    st.subheader("🍽️ Alimentação")
    h_a = st.time_input("Hora:", datetime.now().time())
    txt_a = st.text_input("O que comeu?")
    if st.button("SALVAR COMIDA"):
        st.session_state.dados.append({"Data": str(datetime.now().date()), "H": h_a.hour + (h_a.minute/60), "Cat": "Ali", "Txt": txt_a, "Tipo": "Ponto"})
        st.success("Salvo!")
        st.session_state.menu = None

# --- GRÁFICO DIÁRIO ---
if st.session_state.dados:
    df = pd.DataFrame(st.session_state.dados)
    hoje = str(datetime.now().date())
    df_h = df[df['Data'] == hoje]
    
    if not df_h.empty:
        st.write("### Seu dia hoje:")
        fig = go.Figure()
        cores = {"Med": "#198754", "OFF": "#dc3545", "Exe": "#ffc107", "Ali": "#0dcaf0"}
        for _, r in df_h.iterrows():
            c = cores.get(r['Cat'], "#000")
            if r.get('H_Fim'):
                fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['H'], r['H_Fim']], mode='lines+text', line=dict(color=c, width=25), text=["", "OFF"]))
            else:
                fig.add_trace(go.Scatter(x=[r['Cat']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=18, color=c), text=[r['Txt']], textposition="middle right", textfont=dict(size=18)))
        fig.update_layout(yaxis=dict(range=[24, 0], dtick=1), height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Planilha", data=csv, file_name='dados.csv')
