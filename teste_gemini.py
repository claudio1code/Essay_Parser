# teste_gemini.py (versão de diagnóstico)
import google.generativeai as genai
import os

print("--- Iniciando diagnóstico da API do Google Gemini ---")

try:
    # Garante a mesma autenticação que o resto do projeto
    credentials_path = 'google-credentials.json'
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"ERRO CRÍTICO: Arquivo de credenciais '{credentials_path}' não foi encontrado.")
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    genai.configure(transport='rest')
    print("✅ Autenticação configurada com sucesso.")

    print("\n...Buscando modelos disponíveis que aceitam imagens (método 'generateContent')...\n")
    
    modelos_disponiveis = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            modelos_disponiveis.append(m.name)
            print(f"  - Modelo encontrado: {m.name}")

    print("\n--- Fim da Lista ---")
    
    if any("vision" in name or "1.5" in name or "flash" in name for name in modelos_disponiveis):
        print("\n🎉 SUCESSO! Modelos com capacidade de visão foram encontrados.")
        print("➡️ PRÓXIMO PASSO: Copie o nome de um dos modelos da lista acima que pareça mais adequado")
        print("   (sugestão: 'gemini-1.5-flash-latest' ou algum que contenha 'vision').")
        print("   E cole esse nome no arquivo 'logica_ia.py'.")
    else:
        print("\n⚠️ ATENÇÃO: Nenhum modelo com nome 'vision' ou '1.5' foi encontrado.")
        print("   Verifique a lista acima e escolha o que parecer mais apropriado.")
        print("   Pode ser que o nome seja diferente para sua conta, como 'gemini-pro-multimodal'.")

except Exception as e:
    print(f"\n❌ ERRO DURANTE O DIAGNÓSTICO: {e}")