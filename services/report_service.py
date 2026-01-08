from io import BytesIO
from typing import Any, Dict, Optional
from docx import Document
from config import Config
from logger import get_logger

logger = get_logger(__name__)

def preencher_e_gerar_docx(
    dados: Dict[str, Any], caminho_template: str = Config.TEMPLATE_DOCX_PATH
) -> Optional[BytesIO]:
    try:
        document = Document(caminho_template)
        comps = dados.get("analise_competencias", {})

        # Dicionário de Substituição (Placeholders -> Valores Reais)
        substituicoes = {
            "{{NOME_ALUNO}}": dados.get("nome_aluno", ""),
            "{{TEMA}}": dados.get("tema_redacao", ""),
            "{{ANO}}": dados.get("ano_turma", ""),      # Vem do app.py
            "{{BIMESTRE}}": dados.get("bimestre", ""),  # Vem do app.py
            "{{NOTA_FINAL}}": str(dados.get("nota_final", 0)),
            "{{COMENTARIOS}}": dados.get("comentarios_gerais", ""),
            "{{ALERTA_ORIGINALIDADE}}": dados.get("alerta_originalidade") or ""
        }

        # Adiciona as notas e textos das competências
        for i in range(1, 6):
            chave_nota = f"{{{{NOTA_C{i}}}}}"      # Ex: {{NOTA_C1}}
            chave_texto = f"{{{{ANALISE_C{i}}}}}"   # Ex: {{ANALISE_C1}}
            
            comp_data = comps.get(f"c{i}", {})
            
            substituicoes[chave_nota] = str(comp_data.get("nota", 0))
            substituicoes[chave_texto] = comp_data.get("analise", "")

        # Função para substituir preservando formatação (cor, negrito, tabela)
        def aplicar_substituicao(paragrafo):
            if "{{" in paragrafo.text:
                for codigo, valor in substituicoes.items():
                    if codigo in paragrafo.text:
                        # Substituição nos 'runs' mantém a cor (ex: Vermelho da nota)
                        for run in paragrafo.runs:
                            if codigo in run.text:
                                run.text = run.text.replace(codigo, str(valor))

        # Aplica no corpo do texto
        for p in document.paragraphs:
            aplicar_substituicao(p)

        # Aplica em tabelas (Cabeçalho e Rodapé estão dentro de tabelas)
        for tabela in document.tables:
            for linha in tabela.rows:
                for celula in linha.cells:
                    for p in celula.paragraphs:
                        aplicar_substituicao(p)

        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)
        return buffer

    except Exception as e:
        logger.error(f"Erro no Word: {e}")
        return None