from io import BytesIO
from typing import Any, Dict, Optional
from docx import Document
from config import Config
from logger import get_logger

logger = get_logger(__name__)

def preencher_e_gerar_docx(
    dados: Dict[str, Any], caminho_template: str = Config.TEMPLATE_DOCX_PATH
) -> Optional[BytesIO]:
    """
    Preenche o template Word com os dados da correção e retorna o arquivo em memória.
    Garante a substituição mesmo que o Word quebre os placeholders internamente.
    """
    try:
        # Abre o template original
        document = Document(caminho_template)
        comps = dados.get("analise_competencias", {})

        # Dicionário de Substituição (Placeholders -> Valores Reais)
        substituicoes = {
            "{{NOME_ALUNO}}": dados.get("nome_aluno", ""),
            "{{TEMA}}": dados.get("tema_redacao", ""),
            "{{ANO}}": dados.get("ano_turma", ""),
            "{{BIMESTRE}}": dados.get("bimestre", ""),
            "{{NOTA_FINAL}}": str(dados.get("nota_final", 0)),
            "{{COMENTARIOS}}": dados.get("comentarios_gerais", ""),
            "{{ALERTA_ORIGINALIDADE}}": dados.get("alerta_originalidade") or ""
        }

        # Adiciona as notas e análises das 5 competências
        for i in range(1, 6):
            chave_nota = f"{{{{NOTA_C{i}}}}}"      
            chave_texto = f"{{{{ANALISE_C{i}}}}}"   
            
            comp_data = comps.get(f"c{i}", {})
            
            substituicoes[chave_nota] = str(comp_data.get("nota", 0))
            # Remove possíveis asteriscos ou # que a IA possa ter enviado por engano
            analise_limpa = comp_data.get("analise", "").replace("**", "").replace("#", "")
            substituicoes[chave_texto] = analise_limpa

        def aplicar_substituicao(paragrafo):
            """
            Lógica robusta: tenta substituir preservando a formatação do run.
            Se falhar (placeholder quebrado pelo Word), força a substituição no parágrafo.
            """
            texto_p = paragrafo.text
            if "{{" in texto_p:
                for codigo, valor in substituicoes.items():
                    if codigo in texto_p:
                        substituiu_no_run = False
                        # 1. Tenta manter a formatação (cores das notas, negritos do cabeçalho)
                        for run in paragrafo.runs:
                            if codigo in run.text:
                                run.text = run.text.replace(codigo, str(valor))
                                substituiu_no_run = True
                        
                        # 2. Se o placeholder estiver "fatiado" entre runs, força a troca no nível do parágrafo
                        if not substituiu_no_run:
                            paragrafo.text = paragrafo.text.replace(codigo, str(valor))
                            # Re-carrega o texto para os próximos placeholders do mesmo parágrafo
                            texto_p = paragrafo.text

        # Processa o corpo do documento
        for p in document.paragraphs:
            aplicar_substituicao(p)

        # Processa as tabelas (Cabeçalho, notas e grade final estão em tabelas no seu template)
        for tabela in document.tables:
            for linha in tabela.rows:
                for celula in linha.cells:
                    for p in celula.paragraphs:
                        aplicar_substituicao(p)

        # Salva o arquivo final em um buffer de memória
        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)
        logger.info(f"✅ Relatório gerado com sucesso para o aluno: {dados.get('nome_aluno')}")
        return buffer

    except Exception as e:
        logger.error(f"❌ Erro ao processar o Word: {e}")
        return None