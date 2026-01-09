"""
Script de teste para verificar se a IA está extraindo os dados corretamente.
Execute: python testar_extracao.py caminho/para/imagem.jpg
"""

import json
import sys
from pathlib import Path
import os

# Adiciona o diretório 'src' ao sys.path para permitir importações diretas
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from app.core.logger import get_logger
from app.services import ai_service

logger = get_logger(__name__)


def testar_com_imagem(caminho_imagem: str):
    """Testa a extração de dados de uma imagem específica."""
    
    print("=" * 70)
    print("🧪 TESTE DE EXTRAÇÃO DE DADOS DA IA")
    print("=" * 70)
    
    # Configura a IA
    try:
        ai_service.configurar_ia()
        print("✅ IA configurada com sucesso\n")
    except Exception as e:
        print(f"❌ Erro ao configurar IA: {e}")
        return False
    
    # Carrega o prompt
    try:
        prompt = ai_service.carregar_prompt()
        print(f"✅ Prompt carregado ({len(prompt)} caracteres)\n")
    except Exception as e:
        print(f"❌ Erro ao carregar prompt: {e}")
        return False
    
    # Verifica se a imagem existe
    caminho_path = Path(caminho_imagem)
    if not caminho_path.exists():
        print(f"❌ Caminho não encontrado: {caminho_imagem}")
        return False
    
    if caminho_path.is_dir():
        print(f"❌ Você passou uma pasta, não um arquivo!")
        print(f"   Pasta: {caminho_imagem}")
        print(f"\n💡 Arquivos de imagem nesta pasta:")
        imagens = list(caminho_path.glob("*.jpg")) + list(caminho_path.glob("*.png")) + list(caminho_path.glob("*.jpeg"))
        if imagens:
            for img in imagens[:5]:
                print(f"   - {img.name}")
            print(f"\n💡 Execute novamente com um destes arquivos:")
            print(f'   python testar_extracao.py "{imagens[0]}"')
        else:
            print("   (Nenhuma imagem .jpg/.png encontrada)")
        return False
    
    print(f"📸 Processando imagem: {caminho_path.name}")
    print("⏳ Aguarde, a IA está analisando...\n")
    
    # Analisa a redação
    dados = ai_service.analisar_redacao(str(caminho_path), prompt)
    
    if not dados:
        print("❌ A IA não retornou dados. Verifique os logs acima.")
        return False
    
    # Exibe os resultados de forma organizada
    print("\n" + "=" * 70)
    print("📊 DADOS EXTRAÍDOS PELA IA")
    print("=" * 70)
    
    print(f"\n👤 Nome do Aluno: {dados.get('nome_aluno', 'NÃO EXTRAÍDO')}")
    print(f"📝 Tema: {dados.get('tema_redacao', 'NÃO EXTRAÍDO')}")
    print(f"📅 Data: {dados.get('data_redacao', 'NÃO EXTRAÍDO')}")
    print(f"📊 Nota Final: {dados.get('nota_final', 'NÃO CALCULADO')}")
    
    print("\n" + "-" * 70)
    print("📋 NOTAS POR COMPETÊNCIA:")
    print("-" * 70)
    
    comps = dados.get('analise_competencias', {})
    total = 0
    for i in range(1, 6):
        comp = comps.get(f'c{i}', {})
        nota = comp.get('nota', 0)
        total += nota
        print(f"  C{i}: {nota} pontos")
    
    print(f"\n  🎯 TOTAL: {total} pontos")
    
    if total != dados.get('nota_final', 0):
        print(f"  ⚠️  ATENÇÃO: Soma manual ({total}) ≠ nota_final ({dados.get('nota_final')})")
    
    # Verifica campos obrigatórios
    print("\n" + "-" * 70)
    print("✅ VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS:")
    print("-" * 70)
    
    campos_criticos = [
        ('nome_aluno', dados.get('nome_aluno')),
        ('tema_redacao', dados.get('tema_redacao')),
        ('data_redacao', dados.get('data_redacao')),
        ('nota_final', dados.get('nota_final')),
        ('comentarios_gerais', dados.get('comentarios_gerais')),
    ]
    
    todos_ok = True
    for campo, valor in campos_criticos:
        if not valor or str(valor).strip() in ['', '0', 'Não identificado', 'null']:
            print(f"  ❌ {campo}: VAZIO ou padrão")
            todos_ok = False
        else:
            preview = str(valor)[:50] + "..." if len(str(valor)) > 50 else str(valor)
            print(f"  ✅ {campo}: {preview}")
    
    # Exibe análise de uma competência como exemplo
    print("\n" + "-" * 70)
    print("📖 EXEMPLO DE ANÁLISE (Competência 1):")
    print("-" * 70)
    c1_analise = comps.get('c1', {}).get('analise', 'Não disponível')
    print(f"\n{c1_analise[:300]}...")
    
    # Salva JSON completo para inspeção
    output_file = "teste_extracao_resultado.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 JSON completo salvo em: {output_file}")
    
    print("\n" + "=" * 70)
    if todos_ok:
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("⚠️  TESTE CONCLUÍDO COM ALERTAS - Verifique os campos marcados")
    print("=" * 70)
    
    return todos_ok


if __name__ == "__main__":
    if len(sys.argv) > 1:
        caminho = sys.argv[1]
    else:
        print("Digite o caminho da imagem de teste:")
        caminho = input("> ").strip()
    
    if not caminho:
        print("❌ Nenhuma imagem fornecida.")
        sys.exit(1)
    
    sucesso = testar_com_imagem(caminho)
    sys.exit(0 if sucesso else 1)