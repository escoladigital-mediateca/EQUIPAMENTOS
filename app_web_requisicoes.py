import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página no navegador
st.set_page_config(
    page_title="Sistema de Requisição de Equipamentos",
    page_icon="🎒",
    layout="wide"
)

FILE_PATH = "requisicoes.csv"

# Função para carregar ou inicializar os dados
def carregar_dados():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH, dtype=str)
    else:
        # Cria a estrutura da base de dados se não existir
        df = pd.DataFrame(columns=[
            "ID_Requisicao", "Numero_Aluno", "Nome_Aluno", 
            "Codigo_Equipamento", "Data_Requisicao", "Data_Devolucao", "Estado"
        ])
        df.to_csv(FILE_PATH, index=False)
        return df

# Função para guardar dados no CSV
def guardar_dados(df):
    df.to_csv(FILE_PATH, index=False)

# Carregar dados atuais
df_requisicoes = carregar_dados()

st.title("🎒 Sistema de Requisição de Equipamentos - Escola")
st.markdown("---")

# Separadores da aplicação (Tabs)
tab_req, tab_dev, tab_hist = st.tabs(["📝 Nova Requisição", "🔄 Devolução", "📋 Histórico & Pendentes"])

# ---------------------------------------------------------
# TAB 1: NOVA REQUIÇÃO
# ---------------------------------------------------------
with tab_req:
    st.header("Registar Nova Requisição")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nome_aluno = st.text_input("Nome do Aluno", placeholder="Ex: João Silva")
        num_aluno = st.text_input("Número do Aluno", placeholder="Ex: 12345")
    
    with col2:
        st.subheader("Leitura do Código do Equipamento")
        metodo_qr = st.radio("Escolha como introduzir o código:", ["Digitar / Leitor USB", "Usar Webcam do Chromebook"], horizontal=True)
        
        codigo_equipamento = ""
        if metodo_qr == "Digitar / Leitor USB":
            codigo_equipamento = st.text_input("Código QR / Código de Barras", placeholder="Aproxime o leitor de código USB...")
        else:
            img_file = st.camera_input("Tire uma foto ao Código QR do equipamento")
            if img_file is not None:
                st.info("💡 Sugestão: Se a leitura por foto automática falhar no browser, podes digitar o código lido na caixa abaixo.")
                codigo_equipamento = st.text_input("Confirmar Código lido da foto:", key="qr_webcam_input")

    st.markdown("---")
    if st.button("✅ Confirmar Requisição", type="primary", use_container_width=True):
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
            st.success(f"Requisição do equipamento '{codigo_equipamento}' registada para {nome_aluno} com sucesso!")
            st.rerun()

# ---------------------------------------------------------
# TAB 2: DEVOLUÇÃO
# ---------------------------------------------------------
with tab_dev:
    st.header("Registar Devolução de Equipamento")
    
    col_dev1, col_dev2 = st.columns(2)
    
    with col_dev1:
        codigo_dev = st.text_input("Código do Equipamento a Devolver", placeholder="Leia ou introduza o código QR...")
        
    with col_dev2:
        st.write("Ou use a câmara:")
        img_dev = st.camera_input("Capturar código para devolução")
        if img_dev is not None and not codigo_dev:
            codigo_dev = st.text_input("Confirmar código para devolução:", key="dev_qr_input")

    if st.button("🔄 Confirmar Devolução", type="primary", use_container_width=True):
        if not codigo_dev:
            st.error("⚠️ Por favor, introduza o código do equipamento!")
        else:
            mask = (df_requisicoes["Codigo_Equipamento"] == codigo_dev) & (df_requisicoes["Estado"] == "Pendente")
            
            if mask.any():
                data_dev = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df_requisicoes.loc[mask, "Data_Devolucao"] = data_dev
                df_requisicoes.loc[mask, "Estado"] = "Devolvido"
                guardar_dados(df_requisicoes)
                st.success(f"Equipamento '{codigo_dev}' devolvido com sucesso em {data_dev}!")
                st.rerun()
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
    
    # Download do ficheiro em Excel/CSV
    csv_data = df_exibir.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descarregar Tabela em CSV",
        data=csv_data,
        file_name=f"requisicoes_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
