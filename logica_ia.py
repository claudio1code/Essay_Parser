# logica_ia.py
import google.generativeai as genai
from PIL import Image
import json
import re
import os

def configurar_ia():
    """
    Configura a autenticação explicitamente apontando para o arquivo de credenciais.
    """
    try:
        credentials_path = 'google-credentials.json'
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"ERRO CRÍTICO: O arquivo de credenciais '{credentials_path}' não foi encontrado.")
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        genai.configure(transport='rest')

    except Exception as e:
        print(f"❌ ERRO ao configurar a API: {e}")
        raise

def carregar_prompt(caminho_prompt="prompt.txt"):
    """Carrega o conteúdo do arquivo de prompt."""
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ ERRO CRÍTICO: O arquivo de prompt '{caminho_prompt}' não foi encontrado.")
        raise

def analisar_redacao(caminho_imagem, prompt):
    """
    Envia a imagem para a IA e retorna a análise como um dicionário Python (de JSON).
    """
    # --- AJUSTE FINAL E DEFINITIVO AQUI ---
    # Usando o nome exato do modelo que a sua API listou.
    model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
    # ------------------------------------
    try:
        img = Image.open(caminho_imagem)
        response = model.generate_content([prompt, img])
        
        resposta_texto = response.text
        json_match = re.search(r'\{.*\}', resposta_texto, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            try:
                dados_redacao = json.loads(json_str)
                return dados_redacao
            except json.JSONDecodeError:
                print(f"❌ ERRO: A IA retornou um JSON inválido. Resposta recebida:\n{json_str}")
                return None
        else:
            print(f"❌ ERRO: Nenhuma estrutura JSON foi encontrada na resposta da IA. Resposta recebida:\n{resposta_texto}")
            return None
            
    except FileNotFoundError:
        print(f"❌ ERRO: A imagem não foi encontrada em '{caminho_imagem}'")
        return None
    except Exception as e:
        print(f"❌ Ocorreu um erro na chamada da API Gemini: {e}")
        return None