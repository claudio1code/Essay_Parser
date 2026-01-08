import json
import os
from typing import Any, Dict, Optional, TypedDict
import google.generativeai as genai
from PIL import Image
from config import Config
from logger import get_logger

logger = get_logger(__name__)

# --- Schema (Mantendo a estrutura simples que combinamos) ---
class DetalheCompetencia(TypedDict):
    nota: int
    analise: str

class AnaliseCompetencias(TypedDict):
    c1: DetalheCompetencia
    c2: DetalheCompetencia
    c3: DetalheCompetencia
    c4: DetalheCompetencia
    c5: DetalheCompetencia

class CorrecaoRedacao(TypedDict):
    nome_aluno: str
    tema_redacao: str
    data_redacao: str
    nota_final: int
    comentarios_gerais: str
    alerta_originalidade: Optional[str]
    analise_competencias: AnaliseCompetencias

def configurar_ia() -> None:
    """
    Configura a autenticação usando a API KEY direta.
    Muito mais simples e menos propenso a erros de arquivo.
    """
    try:
        # Tenta pegar a chave do .env
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            # Fallback: Se não tiver API Key, tenta o método antigo do JSON (para compatibilidade)
            # Mas recomendo usar a API Key
            logger.warning("GEMINI_API_KEY não encontrada. Tentando método legado (JSON)...")
            cred_file = Config.GOOGLE_CREDENTIALS_PATH
            if os.path.exists(cred_file):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_file
            else:
                raise ValueError("Nenhuma chave de API ou arquivo de credenciais encontrado.")
        
        # Configura a lib com a chave
        if api_key:
            genai.configure(api_key=api_key)
            
        logger.info("IA Configurada com sucesso (Método API Key).")

    except Exception as e:
        logger.error(f"Erro ao configurar a API: {e}")
        raise

def carregar_prompt(caminho_prompt: str = Config.PROMPT_PATH) -> str:
    with open(caminho_prompt, "r", encoding="utf-8") as f:
        return f.read()

def analisar_redacao(caminho_imagem: str, prompt: str) -> Optional[Dict[str, Any]]:
    try:
        # Configuração para resposta JSON garantida
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json", 
            response_schema=CorrecaoRedacao
        )
        
        # Instancia o modelo
        model = genai.GenerativeModel(
            model_name=Config.MODEL_NAME, 
            generation_config=generation_config
        )
        
        if not os.path.exists(caminho_imagem):
            logger.error("Imagem não encontrada.")
            return None
            
        img = Image.open(caminho_imagem)
        
        # Envia para o Gemini
        response = model.generate_content([prompt, img])
        
        return json.loads(response.text)
    
    except Exception as e:
        logger.error(f"Erro na chamada da IA: {e}")
        return None