import json
import os
from typing import List, Dict

from app.core.logger import get_logger
from config import Config

logger = get_logger(__name__)

FEEDBACK_FILE = os.path.join(Config.BASE_DIR, "data", "feedback_ocr.json")


def carregar_feedbacks() -> List[Dict[str, str]]:
    """Carrega o histórico de feedbacks do usuário."""
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar feedbacks: {e}")
        return []


def salvar_feedback(lido_errado: str, lido_certo: str) -> bool:
    """Salva uma nova correção feita pelo professor/usuário."""
    try:
        # Garante que o diretório exista
        os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
        
        feedbacks = carregar_feedbacks()
        
        # Evita duplicatas exatas
        novo_item = {"errado": lido_errado.strip(), "certo": lido_certo.strip()}
        if novo_item not in feedbacks:
            feedbacks.append(novo_item)
            
            with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
                json.dump(feedbacks, f, ensure_ascii=False, indent=4)
            logger.info(f"Feedback salvo: '{lido_errado}' -> '{lido_certo}'")
            return True
        return False
    except Exception as e:
        logger.error(f"Erro ao salvar feedback: {e}")
        return False

def formatar_historico_para_prompt() -> str:
    """Formata os feedbacks para serem injetados no prompt do Gemini."""
    feedbacks = carregar_feedbacks()
    if not feedbacks:
        return ""
    
    texto = "\n\n--- HISTÓRICO DE APRENDIZADO (SEUS ERROS DE OCR PASSADOS) ---\n"
    texto += "Aprenda com seus erros anteriores de transcrição de caligrafia. "
    texto += "Quando você encontrar as palavras da esquerda visualmente, saiba que o contexto correto é a palavra da direita. "
    texto += "NÃO tire pontos do aluno por caligrafia nestes casos documentados:\n"
    
    # Limita aos últimos 20 feedbacks para não explodir o prompt (In-Context Learning costuma bastar com poucos exemplos)
    recentes = feedbacks[-20:]
    for f in recentes:
        texto += f'- "{f["errado"]}" -> na verdade era "{f["certo"]}"\n'
        
    return texto
