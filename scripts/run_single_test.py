import os
import sys
import argparse

# Adiciona o diretório 'src' ao sys.path para permitir importações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from app.core.logger import get_logger
from app.services import ai_service, report_service

# --- Configuração ---
logger = get_logger(__name__)
OUTPUT_FILENAME = os.path.join(Config.TMP_DIR, "test_output.docx")

def run_test(image_path: str):
    """
    Executa um teste de ponta a ponta: analisa uma imagem de redação,
    gera um relatório .docx e o salva em um local temporário.
    """
    logger.info("--- INICIANDO TESTE DE GERAÇÃO DE RELATÓRIO ---")

    # 1. Verifica se a imagem de entrada existe
    if not os.path.exists(image_path):
        logger.error(f"Imagem de teste não encontrada em: {image_path}")
        return False

    logger.info(f"Imagem de teste: {image_path}")

    # 2. Configura a IA e carrega o prompt
    try:
        ai_service.configurar_ia()
        prompt = ai_service.carregar_prompt()
        logger.info("Serviço de IA configurado e prompt carregado.")
    except Exception as e:
        logger.error(f"Falha ao inicializar o serviço de IA: {e}")
        return False

    # 3. Analisa a redação para obter os dados
    logger.info("Analisando a imagem da redação com a IA...")
    dados_redacao = ai_service.analisar_redacao(image_path, prompt)
    if not dados_redacao:
        logger.error("A análise da IA não retornou dados.")
        return False
    
    logger.info(f"Análise concluída. Aluno: {dados_redacao.get('nome_aluno')}, Nota: {dados_redacao.get('nota_final')}")

    # 4. Gera o arquivo .docx
    logger.info("Gerando o relatório .docx...")
    arquivo_docx_bytes = report_service.preencher_e_gerar_docx(dados_redacao)
    if not arquivo_docx_bytes:
        logger.error("A geração do .docx falhou.")
        return False

    # 5. Salva o arquivo .docx gerado
    try:
        with open(OUTPUT_FILENAME, "wb") as f:
            f.write(arquivo_docx_bytes.getbuffer())
        logger.info(f"Relatório salvo com sucesso em: {OUTPUT_FILENAME}")
    except Exception as e:
        logger.error(f"Falha ao salvar o arquivo .docx: {e}")
        return False

    logger.info("--- TESTE CONCLUÍDO ---")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa um teste de correção de redação.")
    parser.add_argument("image_path", type=str, help="Caminho para a imagem da redação a ser testada.")
    args = parser.parse_args()
    
    run_test(args.image_path)
