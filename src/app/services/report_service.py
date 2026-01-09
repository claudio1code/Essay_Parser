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
    Preenche um template .docx com os dados da redação e retorna o arquivo em memória.
    Utiliza uma abordagem de substituição de texto robusta.
    """
    try:
        document = Document(caminho_template)
        comps = dados.get("analise_competencias", {})

        # Dicionário de Placeholders
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
            chave_nota = f"{{{{NOTA_C{i}}}}}"
            chave_texto = f"{{{{ANALISE_C{i}}}}}"
            comp_data = comps.get(f"c{i}", {})
            substituicoes[chave_nota] = str(comp_data.get("nota", 0))
            analise_limpa = comp_data.get("analise", "").replace("**", "").replace("#", "")
            substituicoes[chave_texto] = analise_limpa

        # --- Lógica de Substituição ---
        # Itera em todos os parágrafos do corpo
        for p in document.paragraphs:
            for codigo, valor in substituicoes.items():
                # Usamos uma abordagem mais simples que substitui no parágrafo inteiro
                # Isso é mais robusto contra 'runs' divididos.
                if codigo in p.text:
                    # Salva a formatação do primeiro 'run'
                    style = p.runs[0].style if p.runs else None
                    font = p.runs[0].font.name if p.runs and p.runs[0].font.name else None
                    
                    # Substitui o texto
                    text = p.text.replace(codigo, str(valor))
                    
                    # Limpa o parágrafo e adiciona o novo texto com a formatação
                    p.clear()
                    run = p.add_run(text)
                    if style:
                        run.style = style
                    if font:
                        run.font.name = font


        # Itera em todas as tabelas
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        for codigo, valor in substituicoes.items():
                            if codigo in p.text:
                                style = p.runs[0].style if p.runs else None
                                font = p.runs[0].font.name if p.runs and p.runs[0].font.name else None
                                text = p.text.replace(codigo, str(valor))
                                p.clear()
                                run = p.add_run(text)
                                if style:
                                    run.style = style
                                if font:
                                    run.font.name = font

        # Itera nos cabeçalhos
        for section in document.sections:
            header = section.header
            for p in header.paragraphs:
                for codigo, valor in substituicoes.items():
                    if codigo in p.text:
                        style = p.runs[0].style if p.runs else None
                        font = p.runs[0].font.name if p.runs and p.runs[0].font.name else None
                        text = p.text.replace(codigo, str(valor))
                        p.clear()
                        run = p.add_run(text)
                        if style:
                            run.style = style
                        if font:
                            run.font.name = font
            for table in header.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            for codigo, valor in substituicoes.items():
                                if codigo in p.text:
                                    style = p.runs[0].style if p.runs else None
                                    font = p.runs[0].font.name if p.runs and p.runs[0].font.name else None
                                    text = p.text.replace(codigo, str(valor))
                                    p.clear()
                                    run = p.add_run(text)
                                    if style:
                                        run.style = style
                                    if font:
                                        run.font.name = font

        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)
        return buffer

    except Exception as e:
        logger.error(f"Erro ao gerar Word: {e}")
        return None