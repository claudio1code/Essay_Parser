import os
import re
import io
import zipfile

import streamlit as st

from app.core.logger import get_logger
from app.core import feedback_manager
from app.services import ai_service, report_service
from app.services.drive_service import GoogleDriveService
from config import Config

# --- Configuração de Logs ---
logger = get_logger(__name__)

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Corretor de Redação Enem", page_icon="")

# --- Funções Utilitárias ---
def extrair_id_drive(url_ou_id):
    """Extrai o ID do arquivo/pasta de uma URL do Google Drive."""
    if not url_ou_id:
        return None
    # Padrão: https://drive.google.com/drive/folders/ID ou direto o ID
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", url_ou_id)
    if match:
        return match.group(1)
    # Se não encontrar, assume que já é o ID
    return url_ou_id

# --- Inicialização do Sistema ---
try:
    ai_service.configurar_ia()

    # Carrega o prompt apenas uma vez na sessão para otimizar
    if "prompt_mestre" not in st.session_state:
        st.session_state["prompt_mestre"] = ai_service.carregar_prompt()
    PROMPT_MESTRE = st.session_state["prompt_mestre"]

except Exception as e:
    st.error(f"Erro Crítico na Inicialização: {e}")
    st.stop()

# --- Cabeçalho Principal ---
st.title(" Corretor de Redação Enem")

# --- BARRA LATERAL (Configurações da Turma) ---
with st.sidebar:
    st.header(" Dados da Turma")
    st.info("Estes dados sairão iguais em todas as redações.")

    entrada_ano = st.text_input("Ano / Turma:", value="3º Ano Ensino Médio")
    entrada_bimestre = st.text_input("Bimestre:", value="1º Bimestre")
    
    st.divider()
    
    st.markdown("### Instruções")
    st.write("1. Escolha entre correção individual ou em lote.")
    st.write("2. No modo individual, envie o arquivo e baixe o resultado.")
    st.write("3. No modo em lote, indique as pastas no seu computador.")
    
    # Bloco LGPD
    st.markdown("---")
    st.markdown(" **Privacidade & LGPD**")
    st.info("Este sistema atua apenas como Operador de dados. As imagens e textos gerados não são utilizados para treinamento de IA de terceiros e são processados de forma efêmera.")

# --- Criação das Abas ---
tab1, tab2, tab3, tab4 = st.tabs(
    [
        " Correção Individual",
        " Lote Local",
        " Lote (Drive)",
        " Treinamento OCR",
    ]
)

# --- ABA 1: CORREÇÃO INDIVIDUAL ---
with tab1:
    st.subheader("Processar uma única imagem")
    
    # Upload da imagem
    imagem_redacao = st.file_uploader(
        "Envie a foto da redação (JPG/PNG)",
        type=["jpg", "jpeg", "png"],
        key="individual"
    )
    
    if imagem_redacao is not None:
        if st.button("Analisar Redação", type="primary", use_container_width=True):
            temp_dir = Config.TMP_DIR
            caminho_img_temp = os.path.join(temp_dir, imagem_redacao.name)
            
            try:
                with open(caminho_img_temp, "wb") as f:
                    f.write(imagem_redacao.getbuffer())
            except Exception as e:
                st.error(f"Erro ao salvar arquivo temporário: {e}")
                st.stop()
            
            with st.spinner("Lendo manuscrito e avaliando competências..."):
                # QR Code temporariamente desabilitado
                dados_aluno_qr = None
                
                # IA analisa o texto da redação
                dados_redacao = ai_service.analisar_redacao(
                    caminho_img_temp, PROMPT_MESTRE
                )
                
                # Deleta a imagem temporária do servidor (LGPD)
                try:
                    if os.path.exists(caminho_img_temp):
                        os.remove(caminho_img_temp)
                except OSError:
                    pass
                
                if dados_redacao:
                    # Se achou o QR Code, ele injeta os dados exatos
                    if dados_aluno_qr:
                        dados_redacao["nome_aluno"] = dados_aluno_qr.get("nome", dados_redacao.get("nome_aluno"))
                        dados_redacao["ano_turma"] = dados_aluno_qr.get("turma", entrada_ano)
                        st.toast(" QR Code detectado! Identificação garantida.")
                    else:
                        dados_redacao["ano_turma"] = entrada_ano
                        st.toast(" QR Code não encontrado. Usando leitura visual da IA.")
                    
                    dados_redacao["bimestre"] = entrada_bimestre
                    
                    # Salva os dados no Session State para a aba de Treinamento OCR
                    st.session_state["ultima_imagem_bytes"] = imagem_redacao.getbuffer().tobytes()
                    st.session_state["ultimo_dados_redacao"] = dados_redacao
                    
                    # DIVISÃO DA TELA: Imagem à Esquerda, Resultados à Direita
                    col_img, col_res = st.columns([1, 1])
                    
                    with col_img:
                        st.subheader(" Imagem Original")
                        st.image(imagem_redacao, use_container_width=True)
                    
                    with col_res:
                        st.success("Análise Concluída!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Aluno", dados_redacao.get("nome_aluno", "N/A"))
                        with col2:
                            st.metric("Nota Final", dados_redacao.get("nota_final", 0))
                        
                        arquivo_docx_bytes = report_service.preencher_e_gerar_docx(
                            dados_redacao
                        )
                        
                        if arquivo_docx_bytes:
                            nome_limpo = dados_redacao.get("nome_aluno", "Aluno").replace(" ", "_")
                            nome_docx = f"Correcao_{nome_limpo}.docx"
                            
                            try:
                                # Tenta pegar a extensão ou usa .jpg por padrão
                                ext_img = os.path.splitext(imagem_redacao.name)[1] if hasattr(imagem_redacao, 'name') else '.jpg'
                                nome_img = f"Correcao_{nome_limpo}{ext_img}"
                                
                                # Cria ZIP com DOCX + imagem
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                    zip_file.writestr(nome_docx, arquivo_docx_bytes.getvalue())
                                    zip_file.writestr(nome_img, imagem_redacao.getbuffer())
                                
                                st.download_button(
                                    label=" Baixar Pacote Completo (ZIP)",
                                    data=zip_buffer.getvalue(),
                                    file_name=f"Correcao_{nome_limpo}.zip",
                                    mime="application/zip",
                                    use_container_width=True,
                                )
                            except Exception as zip_err:
                                logger.error(f"Erro ao gerar ZIP isolado: {zip_err}")
                                st.error(f"Erro interno ao gerar pacote ZIP: {zip_err}")
                                # Fallback para baixar só o DOCX
                                st.download_button(
                                    label=" Baixar Apenas Relatório (.docx)",
                                    data=arquivo_docx_bytes,
                                    file_name=nome_docx,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    use_container_width=True,
                                )
                    
                    st.divider()
                    st.info(" **Visualizou algum erro de leitura da IA na redação?** \nVá para a aba **' Treinamento OCR'** no topo da página para corrigir as palavras lidas incorretamente devido à caligrafia.")
                else:
                    st.error("Falha ao analisar. Verifique os logs.")

# --- ABA 2: CORREÇÃO EM LOTE LOCAL ---
with tab2:
    st.subheader("Processar pasta inteira do computador")
    st.write("Funcionalidade em desenvolvimento")

# --- ABA 3: CORREÇÃO EM LOTE GOOGLE DRIVE ---
with tab3:
    st.subheader("Processar via Google Drive")
    st.write("Funcionalidade em desenvolvimento")

# --- ABA 4: TREINAMENTO OCR ---
with tab4:
    st.subheader("Treinar a IA para ler melhor sua caligrafia")
    st.write("Funcionalidade em desenvolvimento")
