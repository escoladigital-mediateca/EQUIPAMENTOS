import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="Sistema de Requisição de Equipamentos",
    page_icon="🎒",
    layout="wide"
)

FILE_PATH = "requisicoes.csv"

# COLUNAS PADRÃO DA BASE DE DADOS
COLUNAS = [
    "ID_Requisicao", "Numero_Aluno", "Nome_Aluno", 
    "Codigo_Equipamento", "Data_Requisicao", "Data_Devolucao", "Estado"
]

def carregar_dados():
    if os.path.exists(FILE_PATH) and os.path.getsize(FILE_PATH) > 0:
        try:
            df = pd.read_csv(FILE_PATH, dtype=str)
            for col in COLUNAS:
                if col not in df.columns:
                    df[col] = ""
            return df
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=COLUNAS)
            df.to_csv(FILE_PATH, index=False)
            return df
    else:
        df = pd.DataFrame(columns=COLUNAS)
        df.to_csv(FILE_PATH, index=False)
        return df

def guardar_dados(df):
    df.to_csv(FILE_PATH, index=False)

df_requisicoes = carregar_dados()

st.title("🎒 Sistema de Requisição de Equipamentos - Escola")
st.markdown("---")

tab_req, tab_dev, tab_hist = st.tabs(["📝 Nova Requisição", "🔄 Devolução", "📋 Histórico & Pendentes"])

# ---------------------------------------------------------
# TAB 1: NOVA REQUISIÇÃO
# ---------------------------------------------------------
with tab_req:
    st.header("Registar Nova Requisição")
    
    # Limpeza segura usando chaves dinâmicas
    if "req_form_id" not in st.session_state:
        st.session_state["req_form_id"] = 0

    form_id = st.session_state["req_form_id"]

    with st.form(key=f"form_requisicao_{form_id}", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_aluno = st.text_input("Nome do Aluno", placeholder="Ex: João Silva", key=f"req_nome_{form_id}")
            num_aluno = st.text_input("Número do Aluno", placeholder="Ex: 12345", key=f"req_num_{form_id}")
        
        with col2:
            codigo_equipamento = st.text_input("Código QR / Código de Barras do Equipamento", placeholder="Leia com o leitor USB ou digite aqui...", key=f"req_codigo_{form_id}")

        btn_submeter = st.form_submit_button("✅ Confirmar Requisição", type="primary", use_container_width=True)

    if btn_submeter:
        nome_limpo = nome_aluno.strip() if nome_aluno else ""
        num_limpo = num_aluno.strip() if num_aluno else ""
        codigo_limpo = codigo_equipamento.strip() if codigo_equipamento else ""

        if not nome_limpo or not num_limpo or not codigo_limpo:
            st.error("⚠️ Por favor, preencha todos os campos obrigatórios (Nome, Número e Código)!")
        else:
            req_id = datetime.now().strftime("%Y%m%d%H%M%S")
            data_req = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            nova_linha = {
                "ID_Requisicao": req_id,
                "Numero_Aluno": num_limpo,
                "Nome_Aluno": nome_limpo,
                "Codigo_Equipamento": codigo_limpo,
                "Data_Requisicao": data_req,
                "Data_Devolucao": "",
                "Estado": "Pendente"
            }
            
            df_requisicoes = pd.concat([df_requisicoes, pd.DataFrame([nova_linha])], ignore_index=True)
            guardar_dados(df_requisicoes)
            
            st.success(f"✅ Requisição do equipamento '{codigo_limpo}' registada para {nome_limpo} com sucesso!")
            
            # Incrementa o ID para reinicializar os campos em branco
            st.session_state["req_form_id"] += 1
            st.rerun()

    # SCANNER DE CÂMARA EM TEMPO REAL
    with st.expander("📷 Usar Câmara do Chromebook como Leitor de Código de Barras / QR"):
        st.write("Aponte a câmara do Chromebook para o código.")
        
        html_code = """
        <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
        <div id="reader" style="width: 100%; max-width: 500px; margin: auto;"></div>
        <div id="result" style="margin-top: 15px; font-weight: bold; font-size: 18px; color: green; text-align: center;"></div>
        <script>
            function onScanSuccess(decodedText, decodedResult) {
                document.getElementById('result').innerText = "Código Detetado: " + decodedText;
            }
            function onScanFailure(error) {
                // ignora erros de procura de frames
            }
            let html5QrcodeScanner = new Html5QrcodeScanner(
                "reader", { fps: 10, qrbox: {width: 250, height: 250} }, false);
            html5QrcodeScanner.render(onScanSuccess, onScanFailure);
        </script>
        """
        components.html(html_code, height=450)

# ---------------------------------------------------------
# TAB 2: DEVOLUÇÃO
# ---------------------------------------------------------
with tab_dev:
    st.header("Registar Devolução de Equipamento")
    
    # Limpeza segura usando chaves dinâmicas
    if "dev_form_id" not in st.session_state:
        st.session_state["dev_form_id"] = 0

    dev_id = st.session_state["dev_form_id"]

    with st.form(key=f"form_devolucao_{dev_id}", clear_on_submit=False):
        codigo_dev = st.text_input(
            "Código do Equipamento a Devolver", 
            placeholder="Leia com o leitor USB ou digite o código...",
            key=f"input_dev_codigo_{dev_id}"
        )
        btn_devolver = st.form_submit_button("🔄 Confirmar Devolução", type="primary", use_container_width=True)

    if btn_devolver:
        codigo_limpo = codigo_dev.strip() if codigo_dev else ""
        
        if not codigo_limpo:
            st.error("⚠️ Por favor, introduza ou leia o código do equipamento!")
        else:
            mask = (df_requisicoes["Codigo_Equipamento"].astype(str).str.strip() == codigo_limpo) & (df_requisicoes["Estado"] == "Pendente")
            
            if mask.any():
                data_dev = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df_requisicoes.loc[mask, "Data_Devolucao"] = data_dev
                df_requisicoes.loc[mask, "Estado"] = "Devolvido"
                guardar_dados(df_requisicoes)
                
                st.success(f"✅ Equipamento '{codigo_limpo}' devolvido com sucesso em {data_dev}!")
                
                # Incrementa o ID para reinicializar o campo em branco
                st.session_state["dev_form_id"] += 1
                st.rerun()
            else:
                st.error(f"❌ Não foi encontrada nenhuma requisição pendente para o código '{codigo_limpo}'.")

# ---------------------------------------------------------
# TAB 3: HISTÓRICO E PENDENTES
# ---------------------------------------------------------
with tab_hist:
    st.header("Consultar Histórico de Requisições")
    
    filtro_estado = st.selectbox("Filtrar por Estado:", ["Todos", "Pendente", "Devolvido"])
    
    df_exibir = df_requisicoes.copy()
    if filtro_estado != "Todos":
        df_exibir = df_exibir[df_exibir["Estado"] == filtro_estado]
        
    st.dataframe(df_exibir, use_container_width=True)
    
    csv_data = df_exibir.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descarregar Tabela em CSV",
        data=csv_data,
        file_name=f"requisicoes_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
