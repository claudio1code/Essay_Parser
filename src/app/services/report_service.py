from io import BytesIO
from typing import Any, Dict, Optional
from docx import Document
from app.core.logger import get_logger
from config import Config

logger = get_logger(__name__)

def preencher_e_gerar_docx(
    dados: Dict[str, Any], caminho_template: str = Config.TEMPLATE_DOCX_PATH
) -> Optional[BytesIO]:
    """
    Preenche um template .docx com uma abordagem HÍBRIDA e simplificada,
    assumindo que o template foi limpo e todos os placeholders são texto simples.
    1.  Usa a lógica padrão do python-docx para substituir placeholders em parágrafos
        e tabelas normais.
    2.  Usa uma busca profunda com XPath para substituir placeholders em elementos
        complexos como CAIXAS DE TEXTO.
    """
    try:
        document = Document(caminho_template)
        comps = dados.get("analise_competencias", {})

        # 1. Prepara o Dicionário de Substituição
        substituicoes = {
            "{{NOME_ALUNO}}": dados.get("nome_aluno", "Não identificado"),
            "{{TEMA}}": dados.get("tema_redacao", ""),
            "{{ANO}}": dados.get("ano_turma", ""),
            "{{BIMESTRE}}": dados.get("bimestre", ""),
            "{{NOTA_FINAL}}": str(dados.get("nota_final", 0)),
            "{{COMENTARIOS}}": dados.get("comentarios_gerais", ""),
            "{{ALERTA_ORIGINALIDADE}}": dados.get("alerta_originalidade") or ""
        }

        for i in range(1, 6):
            key_nota = "{{NOTA_C{}}}".format(i)
            substituicoes[key_nota] = str(comps.get(f"c{i}", {}).get("nota", 0))
            analise = comps.get(f"c{i}", {}).get("analise", "").replace("**", "")
            key_analise = "{{ANALISE_C{}}}".format(i)
            substituicoes[key_analise] = analise

        # --- ABORDAGEM 1: LÓGICA PADRÃO (Para o corpo do texto) ---
        # Agora que o template está limpo, podemos usar uma abordagem mais direta.
        # Isso pode resetar a formatação do parágrafo, mas garante a substituição.
        todos_paragrafos = list(document.paragraphs)
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    todos_paragrafos.extend(cell.paragraphs)
        for section in document.sections:
            todos_paragrafos.extend(section.header.paragraphs)
            for table in section.header.tables:
                for row in table.rows:
                    for cell in row.cells:
                        todos_paragrafos.extend(cell.paragraphs)
            todos_paragrafos.extend(section.footer.paragraphs)

        for p in todos_paragrafos:
            if not p.text.strip():
                continue
            for codigo, valor in substituicoes.items():
                if codigo in p.text:
                    p.text = p.text.replace(codigo, str(valor))

        # --- ABORDAGEM 2: LÓGICA XPATH (Para Caixas de Texto) ---
        # Executa como um finalizador para pegar o que a primeira abordagem não viu.
        for element in document._element.xpath('.//w:t'):
            for codigo, valor in substituicoes.items():
                if codigo in element.text:
                    element.text = element.text.replace(codigo, str(valor))

        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)
        logger.info(f"✅ Relatório preenchido para: {dados.get('nome_aluno')}")
        return buffer

    except Exception as e:
        logger.error(f"❌ Erro crítico no Word: {e}")
        return None
