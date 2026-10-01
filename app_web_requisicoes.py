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
    # Verifica se o ficheiro existe e se NÃO está vazio (tamanho > 0 bytes)
    if os.path.exists(FILE_PATH) and os.path.getsize(FILE_PATH) > 0:
        try:
            return pd.read_csv(FILE_PATH, dtype=str)
        except pd.errors.EmptyDataError:
            # Se der erro de ficheiro vazio, recria o DataFrame
            df = pd.DataFrame(columns=COLUNAS)
            df.to_csv(FILE_PATH, index=False)
            return df
    else:
        # Cria novo ficheiro com cabeçalhos se não existir ou estiver vazio
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
    
    with st.form(key="form_requisicao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_aluno = st.text_input("Nome do Aluno", placeholder="Ex: João Silva")
            num_aluno = st.text_input("Número do Aluno", placeholder="Ex: 12345")
        
        with col2:
            codigo_equipamento = st.text_input("Código QR / Código de Barras do Equipamento", placeholder="Leia com o leitor USB ou digite aqui...")

        btn_submeter = st.form_submit_button("✅ Confirmar Requisição", type="primary", use_container_width=True)

    if btn_submeter:
        if not nome_aluno or not num_aluno or not codigo_equipamento:
            st.error("⚠️ Por favor, preencha todos os campos obrigatórios!")
        else:
            req_id = datetime.now().strftime("%Y%m%d%H%M%S")
            data_req = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            nova_linha = {
                "ID_Requisicao": req_id,
                "Numero_Aluno": num_aluno,
                "Nome_Aluno": nome_aluno,
                "Codigo_Equipamento": codigo_equipamento,
                "Data_Requisicao": data_req,
                "Data_Devolucao": "",
                "Estado": "Pendente"
            }
            
            df_requisicoes = pd.concat([df_requisicoes, pd.DataFrame([nova_linha])], ignore_index=True)
            guardar_dados(df_requisicoes)
            st.success(f"✅ Requisição do equipamento '{codigo_equipamento}' registada para {nome_aluno} com sucesso!")

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
    
    with st.form(key="form_devolucao", clear_on_submit=True):
        codigo_dev = st.text_input("Código do Equipamento a Devolver", placeholder="Leia com leitor USB ou digite o código...")
        btn_devolver = st.form_submit_button("🔄 Confirmar Devolução", type="primary", use_container_width=True)

    if btn_devolver:
        if not codigo_dev:
            st.error("⚠️ Por favor, introduza o código do equipamento!")
        else:
            mask = (df_requisicoes["Codigo_Equipamento"] == codigo_dev) & (df_requisicoes["Estado"] == "Pendente")
            
            if mask.any():
                data_dev = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df_requisicoes.loc[mask, "Data_Devolucao"] = data_dev
                df_requisicoes.loc[mask, "Estado"] = "Devolvido"
                guardar_dados(df_requisicoes)
                st.success(f"✅ Equipamento '{codigo_dev}' devolvido com sucesso em {data_dev}!")
            else:
                st.error(f"❌ Não foi encontrada nenhuma requisição pendente para o código '{codigo_dev}'.")

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
