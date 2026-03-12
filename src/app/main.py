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
st.set_page_config(layout="wide", page_title="Corretor de Redação Enem", page_icon="📝")


# --- Funções Utilitárias ---
def extrair_id_drive(url_ou_id):
    """Extrai o ID de uma pasta do Google Drive a partir da URL ou retorna o próprio ID."""
    if not url_ou_id:
        return None
    # Regex para capturar o ID na URL do Drive
    match = re.search(r"folders/([a-zA-Z0-9-_]+)", url_ou_id)
    if match:
        return match.group(1)
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
st.title("📝 Corretor de Redação Enem")

# --- BARRA LATERAL (Configurações da Turma) ---
with st.sidebar:
    st.header("🏫 Dados da Turma")
    st.info("Estes dados sairão iguais em todas as redações.")

    entrada_ano = st.text_input("Ano / Turma:", value="3º Ano Ensino Médio")
    entrada_bimestre = st.text_input("Bimestre:", value="1º Bimestre")
    st.divider()
    st.markdown("### Instruções")
    st.write("1. Escolha entre correção individual ou em lote.")
    st.write("2. No modo individual, envie o arquivo e baixe o resultado.")
    st.write("3. No modo em lote, indique as pastas no seu computador.")

# --- Criação das Abas ---
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📄 Correção Individual",
        "📂 Correção em Lote Local",
        "☁️ Correção em Lote (Drive)",
        "🎓 Treinamento OCR",
    ]
)

# --- ABA 1: CORREÇÃO INDIVIDUAL ---
with tab1:
    st.subheader("Processar uma única imagem")
    imagem_redacao = st.file_uploader(
        "Faça o upload da foto da redação",
        type=["jpg", "png", "jpeg"],
        key="individual",
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
                dados_redacao = ai_service.analisar_redacao(
                    caminho_img_temp, PROMPT_MESTRE
                )

                try:
                    if os.path.exists(caminho_img_temp):
                        os.remove(caminho_img_temp)
                except OSError:
                    pass

                if dados_redacao:
                    dados_redacao["ano_turma"] = entrada_ano
                    dados_redacao["bimestre"] = entrada_bimestre

                    # Salva os dados no Session State para a aba de Treinamento OCR
                    st.session_state["ultima_imagem_bytes"] = imagem_redacao.getbuffer().tobytes()
                    st.session_state["ultimo_dados_redacao"] = dados_redacao

                    # DIVISÃO DA TELA: Imagem à Esquerda, Resultados à Direita
                    col_img, col_res = st.columns([1, 1])

                    with col_img:
                        st.subheader("🖼️ Imagem Original")
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
                                nome_zip = f"Correcao_{nome_limpo}.zip"

                                # Garante bytes da imagem
                                img_bytes = imagem_redacao.getbuffer().tobytes()

                                # Criando o arquivo ZIP em memória
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                                    zip_file.writestr(nome_docx, arquivo_docx_bytes.getvalue())
                                    zip_file.writestr(nome_img, img_bytes)
                                
                                st.download_button(
                                    label="📦 Baixar Pacote (DOCX + Imagem)",
                                    data=zip_buffer.getvalue(),
                                    file_name=nome_zip,
                                    mime="application/zip",
                                    use_container_width=True,
                                )
                            except Exception as zip_err:
                                logger.error(f"Erro ao gerar ZIP isolado: {zip_err}")
                                st.error(f"Erro interno ao gerar pacote ZIP: {zip_err}")
                                # Fallback para baixar só o DOCX
                                st.download_button(
                                    label="📥 Baixar Apenas Relatório (.docx)",
                                    data=arquivo_docx_bytes,
                                    file_name=nome_docx,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    use_container_width=True,
                                )

                        st.divider()
                        st.info("💡 **Visualizou algum erro de leitura da IA na redação?** \nVá para a aba **'🎓 Treinamento OCR'** no topo da página para corrigir as palavras lidas incorretamente devido à caligrafia.")

                else:
                    st.error("Falha ao analisar. Verifique os logs.")

# --- ABA 2: CORREÇÃO EM LOTE LOCAL ---
with tab2:
    st.subheader("Processar pasta inteira do computador")
    st.warning(
        "Atenção: Certifique-se de que o caminho das pastas esteja correto e acessível."
    )

    col_input, col_output = st.columns(2)

    with col_input:
        pasta_entrada = st.text_input(
            "Caminho da Pasta de Entrada (Imagens):",
            value=st.session_state.get("pasta_entrada", ""),
            placeholder="/caminho/completo/para/as/fotos",
        )
        if pasta_entrada:
            st.session_state["pasta_entrada"] = pasta_entrada

    with col_output:
        pasta_saida = st.text_input(
            "Caminho da Pasta de Saída (Resultados):",
            value=st.session_state.get("pasta_saida", ""),
            placeholder="/caminho/completo/para/salvar/docx",
        )
        if pasta_saida:
            st.session_state["pasta_saida"] = pasta_saida

    if st.button(
        "Iniciar Processamento em Lote", type="primary", use_container_width=True
    ):
        if not pasta_entrada or not pasta_saida:
            st.warning("Por favor, preencha os caminhos de entrada e saída.")
        elif not os.path.exists(pasta_entrada):
            st.error("A pasta de entrada não existe.")
        else:
            if not os.path.exists(pasta_saida):
                os.makedirs(pasta_saida)
                st.info(f"Pasta de saída criada: {pasta_saida}")

            # Lista arquivos de imagem
            arquivos = [
                f
                for f in os.listdir(pasta_entrada)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]

            if not arquivos:
                st.warning("Nenhuma imagem (JPG, PNG) encontrada na pasta de entrada.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                log_container = st.container()

                sucessos = 0
                erros = 0

                for i, nome_arquivo in enumerate(arquivos):
                    caminho_completo = os.path.join(pasta_entrada, nome_arquivo)
                    status_text.text(
                        f"Processando ({i + 1}/{len(arquivos)}): {nome_arquivo}"
                    )

                    try:
                        # 1. IA analisa
                        dados_redacao = ai_service.analisar_redacao(
                            caminho_completo, PROMPT_MESTRE
                        )

                        if dados_redacao:
                            # 2. Injeta dados da turma
                            dados_redacao["ano_turma"] = entrada_ano
                            dados_redacao["bimestre"] = entrada_bimestre

                            # 3. Gera DOCX
                            doc_buffer = report_service.preencher_e_gerar_docx(
                                dados_redacao
                            )

                            if doc_buffer:
                                # 4. Salva no disco local
                                nome_aluno = dados_redacao.get(
                                    "nome_aluno", f"Aluno_{i}"
                                ).replace(" ", "_")
                                caminho_doc_saida = os.path.join(
                                    pasta_saida, f"Correcao_{nome_aluno}.docx"
                                )

                                with open(caminho_doc_saida, "wb") as f:
                                    f.write(doc_buffer.getbuffer())

                                sucessos += 1
                                log_container.success(
                                    f"✅ Sucesso: {nome_arquivo} -> {nome_aluno}"
                                )
                            else:
                                erros += 1
                                log_container.error(
                                    f"❌ Erro ao gerar DOCX para: {nome_arquivo}"
                                )
                        else:
                            erros += 1
                            log_container.error(f"❌ Falha na IA para: {nome_arquivo}")

                    except Exception as e:
                        erros += 1
                        log_container.error(
                            f"💥 Erro inesperado em {nome_arquivo}: {e}"
                        )

                    # Atualiza progresso
                    progress_bar.progress((i + 1) / len(arquivos))

                st.divider()
                st.success(
                    f"Processamento concluído! Sucessos: {sucessos}, Erros: {erros}"
                )
                st.info(f"Os arquivos corrigidos estão em: {pasta_saida}")

# --- ABA 3: CORREÇÃO EM LOTE DRIVE ---
with tab3:
    st.subheader("Processar pastas do Google Drive")
    st.info(
        "Cole o link da pasta do Drive. O sistema identificará o ID automaticamente."
    )

    url_entrada_drive = st.text_input(
        "Link da Pasta de Entrada (Google Drive):",
        placeholder="https://drive.google.com/drive/folders/...",
        key="drive_in",
    )

    url_saida_drive = st.text_input(
        "Link da Pasta de Saída (Google Drive):",
        placeholder="https://drive.google.com/drive/folders/...",
        key="drive_out",
    )

    if st.button(
        "Iniciar Processamento Cloud", type="primary", use_container_width=True
    ):
        id_entrada = extrair_id_drive(url_entrada_drive)
        id_saida = extrair_id_drive(url_saida_drive)

        if not id_entrada or not id_saida:
            st.warning("Por favor, forneça links válidos para as pastas do Drive.")
        else:
            try:
                with st.spinner("Conectando ao Google Drive..."):
                    drive_service = GoogleDriveService()
                    itens = drive_service.list_pending_images(id_entrada)

                if not itens:
                    st.warning("Nenhuma imagem encontrada na pasta do Drive informada.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    log_container = st.container()

                    sucessos_drive = 0
                    erros_drive = 0

                    for i, item in enumerate(itens):
                        file_id = item["id"]
                        file_name = item["name"]
                        status_text.text(
                            f"Processando ({i + 1}/{len(itens)}): {file_name}"
                        )

                        caminho_temp = os.path.join(Config.TMP_DIR, file_name)

                        try:
                            # 1. Download
                            conteudo = drive_service.download_file(file_id)
                            with open(caminho_temp, "wb") as f:
                                f.write(conteudo)

                            # 2. IA
                            dados = ai_service.analisar_redacao(
                                caminho_temp, PROMPT_MESTRE
                            )

                            if dados:
                                dados["ano_turma"] = entrada_ano
                                dados["bimestre"] = entrada_bimestre

                                # 3. DOCX
                                doc_buffer = report_service.preencher_e_gerar_docx(
                                    dados
                                )

                                if doc_buffer:
                                    # 4. Upload
                                    nome_aluno = dados.get(
                                        "nome_aluno", f"Aluno_{i}"
                                    ).replace(" ", "_")
                                    nome_final = f"Correcao_{nome_aluno}.docx"

                                    novo_id = drive_service.upload_docx(
                                        doc_buffer, nome_final, id_saida
                                    )

                                    if novo_id:
                                        sucessos_drive += 1
                                        log_container.success(
                                            f"✅ Sucesso: {file_name} enviado para o Drive."
                                        )
                                    else:
                                        erros_drive += 1
                                        log_container.error(
                                            f"❌ Falha no upload: {file_name}"
                                        )
                                else:
                                    erros_drive += 1
                                    log_container.error(
                                        f"❌ Erro ao gerar DOCX: {file_name}"
                                    )
                            else:
                                erros_drive += 1
                                log_container.error(f"❌ Falha na IA: {file_name}")

                        except Exception as e:
                            erros_drive += 1
                            log_container.error(f"💥 Erro em {file_name}: {e}")
                        finally:
                            if os.path.exists(caminho_temp):
                                os.remove(caminho_temp)

                        progress_bar.progress((i + 1) / len(itens))

                    st.success(
                        f"Concluído! Sucessos: {sucessos_drive}, Erros: {erros_drive}"
                    )

            except Exception as drive_err:
                st.error(f"Erro ao acessar o Google Drive: {drive_err}")

# --- ABA 4: TREINAMENTO OCR ---
with tab4:
    st.subheader("🎓 Treinamento de Leitura (OCR)")
    st.write(
        "Esta área é dedicada à correção de falhas de Visão Computacional da IA. "
        "Aqui você pode comparar a última imagem processada com os resultados gerados."
    )

    if "ultima_imagem_bytes" in st.session_state and "ultimo_dados_redacao" in st.session_state:
        # Layout Lado a Lado para Leitura
        col_img_treino, col_texto_treino = st.columns([1, 1])

        with col_img_treino:
            st.image(st.session_state["ultima_imagem_bytes"], use_container_width=True)

        with col_texto_treino:
            dados = st.session_state["ultimo_dados_redacao"]
            st.info(f"**Aluno em Avaliação:** {dados.get('nome_aluno', 'N/A')}")
            
            st.markdown("### Comentários Gerais da IA")
            st.write(dados.get("comentarios_gerais", "Sem comentários gerais disponíveis."))
            
            st.markdown("### Análise por Competência")
            competencias = dados.get("analise_competencias", {})
            for key, comp_data in competencias.items():
                with st.expander(f"Competência {key.upper()} - Nota: {comp_data.get('nota', 0)}", expanded=False):
                    st.write(comp_data.get("analise", "Análise não disponível."))

            st.divider()
            st.subheader("🧠 Ensinar a IA")
            st.write("Ensine o significado correto das palavras distorcidas pela caligrafia.")
            
            with st.form("form_treino_ocr", clear_on_submit=True):
                col_err, col_cert = st.columns(2)
                with col_err:
                    lido_errado = st.text_input("O que a IA leu (Errado):", placeholder="ex: eraí")
                with col_cert:
                    lido_certo = st.text_input("O que o aluno escreveu (Certo):", placeholder="ex: era")
                    
                submit_treino = st.form_submit_button("Salvar Correção e Ensinar IA", use_container_width=True, type="primary")
                
                if submit_treino:
                    if lido_errado and lido_certo:
                        sucesso = feedback_manager.salvar_feedback(lido_errado, lido_certo)
                        if sucesso:
                            st.success(f"Feedback salvo! A IA não cometerá o erro '{lido_errado}' novamente.")
                        else:
                            st.warning("Esse feedback já estava registrado ou ocorreu um erro interno.")
                    else:
                        st.error("Preencha as duas palavras do formulário.")
    else:
        st.warning("Nenhuma redação foi analisada recentemente nesta sessão. Vá para a aba 'Correção Individual' e processe uma redação primeiro.")

