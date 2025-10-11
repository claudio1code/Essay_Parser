# corrigir_em_lote.py
import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

import logica_ia
import gerador_docx

# --- Constantes ---
SCOPES = ["https://www.googleapis.com/auth/drive"]
ID_PASTA_ENTRADA = "1c_8ybbo6HAhMxlOeNKX71PPF8TfySKx-"
ID_PASTA_SAIDA = "16xRIPkBY8gRp9vNzxgH1Ex4GhTnkzbed"
TEMP_DIR = "temp_lote"

def autenticar_drive():
    """Autentica com a API do Google Drive."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def main():
    print("Iniciando assistente de correção em lote...")
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    try:
        # --- 1. CONFIGURAÇÃO INICIAL ---
        logica_ia.configurar_ia() # <-- CHAMA A NOVA FUNÇÃO
        print("✅ Autenticação com API Gemini configurada.")
        
        creds_drive = autenticar_drive()
        service_drive = build("drive", "v3", credentials=creds_drive)
        print("✅ Autenticação com Google Drive bem-sucedida.")
        
        prompt = logica_ia.carregar_prompt()
        print("✅ Prompt da IA carregado.")

        # --- O resto do código continua o mesmo ---
        query = f"'{ID_PASTA_ENTRADA}' in parents and (mimeType='image/jpeg' or mimeType='image/png')"
        results = service_drive.files().list(q=query, fields="files(id, name)").execute()
        items = results.get("files", [])

        if not items:
            print("ℹ️ Nenhuma nova redação encontrada para corrigir.")
            return
        print(f"✅ Encontradas {len(items)} redações para corrigir.\n")

        for item in items:
            file_id, file_name = item["id"], item["name"]
            print(f"--- Processando: {file_name} ---")

            caminho_imagem_temp = os.path.join(TEMP_DIR, file_name)

            request = service_drive.files().get_media(fileId=file_id)
            with open(caminho_imagem_temp, "wb") as f:
                f.write(request.execute())
            
            dados_redacao = logica_ia.analisar_redacao(caminho_imagem_temp, prompt)
            
            if not dados_redacao:
                print(f"   ❗️ Erro na análise da IA. Pulando.")
                os.remove(caminho_imagem_temp)
                continue

            arquivo_docx_bytes = gerador_docx.preencher_e_gerar_docx(dados_redacao, 'template.docx')
            
            if not arquivo_docx_bytes:
                print(f"   ❗️ Falha ao gerar o arquivo .docx. Pulando.")
                os.remove(caminho_imagem_temp)
                continue
            
            nome_aluno = dados_redacao.get('nome_aluno', 'Aluno').replace(' ', '_')
            nome_arquivo_final = f"Correcao_{nome_aluno}_{file_id[:6]}.docx"
            
            file_metadata = {"name": nome_arquivo_final, "parents": [ID_PASTA_SAIDA]}
            media = MediaIoBaseUpload(arquivo_docx_bytes, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            
            service_drive.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print(f"   ✅ Relatório de '{nome_aluno}' salvo com sucesso no Drive!\n")

            os.remove(caminho_imagem_temp)

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()