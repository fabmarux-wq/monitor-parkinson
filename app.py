import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração Totalmente Simples
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

# 2. Botões Gigantes para clicar fácil
st.markdown("""
<style>
    .stButton > button { 
        height: 110px !important; 
        font-size: 28px !important; 
        font-weight: bold !important; 
        border-radius: 25px;
        margin-bottom: 15px;
        border: 4px solid #f0f2f6 !important;
    }
</style>
""", unsafe_allow_stdio=True)

st.title("⏱️ Registro Instantâneo")

# 3. Memória Blindada contra Type Error
if 'dados' not in st.session_state:
    st.session_state.dados = []

# Função que salva apenas texto e números simples (evita o erro)
def salvar_clique(categoria, o_que):
    agora = datetime.now()
    # Salvamos como texto puro para o computador não se confundir
    novo_registro = {
        "Data": agora.strftime("%d/%m/%Y"),
        "Hora": agora.strftime("%H:%M"),
        "Minutos": float(agora.hour * 60 + agora.minute),
        "Categoria": str(categoria),
        "Descricao": str(o_que)
    }
    st.session_state.dados.append(novo_registro)
    st.toast(f"✅ Salvo: {o_que}")

# --- BOTÕES DE UM CLIQUE ---
st.write("### Toque para salvar agora:")

col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 PROLOPA", use_container_width=True):
        salvar_clique("Remédio", "Prolopa")
    if st.button("🟡 TREINO", use_container_width=True):
        salvar_clique("Exercício", "Treino")

with col2:
    if st.button("🔴 OFF", use_container_width=True):
        salvar_clique("Estado", "Início OFF")
    if st.button("🔵 COMIDA", use_container_width=True):
        salvar_clique("Alimentação", "Refeição")

# --- LISTA DOS ÚLTIMOS REGISTROS ---
st.markdown("---")
if st.session_state.dados:
    st.write("### Registros de hoje:")
    # Mostra uma tabela simples que não trava
    dados_invertidos = st.session_state.dados[::-1] # O mais novo em cima
    for item in dados_invertidos:
        st.write(f"🕒 **{item['Hora']}** - {item['Categoria']}: {item['Descricao']}")
else:
    st.info("Nada registrado ainda. Toque nos botões acima!")

# --- BOTÃO PARA LIMPAR O ERRO DEFINITIVAMENTE ---
st.markdown("---")
if st.button("🗑️ LIMPAR MEMÓRIA E REINICIAR", use_container_width=True):
    st.session_state.dados = []
    st.rerun()
