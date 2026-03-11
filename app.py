import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Configurações de tela para evitar movimentos indesejados
st.set_page_config(page_title="Monitor Parkinson", layout="centered")

st.markdown("### 📊 Monitor Parkinson Pro")

# Inicializa a memória
if 'dados' not in st.session_state:
    st.session_state.dados = []
if 'menu' not in st.session_state:
    st.session_state.menu = None

# --- BOTÕES DE ATALHO (MAIORES) ---
st.write("📋 **Registrar agora:**")
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

# --- FORMULÁRIOS (ENTRADA SIMPLIFICADA PARA NÃO TRAVAR) ---
if st.session_state.menu:
    st.info(f"Editando: {st.session_state.menu}")
    # Campos de hora simplificados
    col_h, col_m = st.columns(2)
    with col_h: h_dig = st.number_input("Hora (0-23)", 0, 23, datetime.now().hour)
    with col_m: m_dig = st.number_input("Minuto (0-59)", 0, 59, datetime.now().minute)
    h_dec = h_dig + (m_dig/60)

    if st.session_state.menu == "Med":
        sel = st.multiselect("Remédios:", ["Prolopa BD (1)", "Mantidan (2)", "Pramipexol (3)", "Rasagilina (4)", "Prolopa HBS (5)", "Prolopa D (6)"])
        if st.button("SALVAR AGORA"):
            for m in sel:
                n = m.split("(")[1].replace(")", "")
                st.session_state.dados.append({"Data": datetime.now().date(), "H": h_dec, "Cat": "Med", "Txt": n, "Tipo": "Ponto"})
            st.session_state.menu = None
            st.success("Salvo!")

    elif st.session_state.menu == "OFF":
        duracao = st.number_input("Duração em minutos:", 15, 240, 30)
        if st.button("SALVAR FIM DO OFF"):
            st.session_state.dados.append({"Data": datetime.now().date(), "H": h_dec, "H_Fim": h_dec + (duracao/60), "Cat": "OFF", "Txt": "!", "Tipo": "Periodo"})
            st.session_state.menu = None
            st.success("Salvo!")

    if st.button("Cancelar"): st.session_state.menu = None

# --- VISUALIZAÇÃO (ABAS) ---
tab_hoje, tab_mes = st.tabs(["📅 Gráfico do Dia", "📅 Histórico do Mês"])

with tab_hoje:
    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        df_h = df[df['Data'] == datetime.now().date()]
        
        if not df_h.empty:
            fig = go.Figure()
            cores = {"Med": "#198754", "OFF": "#dc3545", "Exe": "#ffc107", "Ali": "#0dcaf0"}
            for _, r in df_h.iterrows():
                c = cores.get(r['Cat'], "#000")
                if 'H_Fim' in r and not pd.isna(r['H_Fim']):
                    fig.add_trace(go.Scatter(x=[r['Cat'], r['Cat']], y=[r['H'], r['H_Fim']], mode='lines', line=dict(color=c, width=30)))
                else:
                    fig.add_trace(go.Scatter(x=[r['Cat']], y=[r['H']], mode='markers+text', marker=dict(symbol='square', size=20, color=c), text=[r['Txt']], textposition="middle right", textfont=dict(size=20)))
            
            # CONFIGURAÇÃO PARA O GRÁFICO FICAR FIXO (SEM ZOOM NO CELULAR)
            fig.update_layout(
                yaxis=dict(range=[24, 0], dtick=1, title="Horas"),
                height=600,
                showlegend=False,
                dragmode=False, # Desativa o arraste que some com o gráfico
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True}) # staticPlot trava o gráfico
        else:
            st.write("Sem registros hoje.")

with tab_mes:
    if st.session_state.dados:
        df_mes = pd.DataFrame(st.session_state.dados)
        st.write("Todos os registros deste mês:")
        st.dataframe(df_mes.sort_values(by=['Data', 'H'], ascending=False), use_container_width=True)
    else:
        st.write("Nenhum dado salvo ainda.")

# Botão de segurança
if st.session_state.dados:
    if st.sidebar.button("Limpar todos os testes"):
        st.session_state.dados = []
        st.rerun()
