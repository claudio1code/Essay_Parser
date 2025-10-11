# app.py
import streamlit as st
import os
import logica_ia
import gerador_docx

# --- Configuração da Página e Inicialização ---
st.set_page_config(layout="wide")
st.title("✍️ Projeto Mae Redação")
st.markdown("Faça o upload da foto de uma redação manuscrita para receber uma análise completa e precisa.")
st.divider()

try:
    logica_ia.configurar_ia() # <-- CHAMA A NOVA FUNÇÃO
    PROMPT_MESTRE = logica_ia.carregar_prompt()
except Exception as e:
    st.error(f"Erro Crítico na Inicialização: {e}")
    st.stop()

# --- Interface do Usuário ---
imagem_redacao = st.file_uploader(
    "Envie a foto da redação aqui (formato .jpg ou .png)",
    type=['jpg', 'png', 'jpeg']
)

if imagem_redacao is not None:
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    caminho_imagem_temp = os.path.join(temp_dir, imagem_redacao.name)
    with open(caminho_imagem_temp, "wb") as f:
        f.write(imagem_redacao.getbuffer())

    if st.button("Analisar Redação com IA", type="primary", use_container_width=True):
        
        with st.spinner("Analisando a imagem e corrigindo a redação..."):
            dados_redacao = logica_ia.analisar_redacao(caminho_imagem_temp, PROMPT_MESTRE)
        
        os.remove(caminho_imagem_temp)

        if dados_redacao:
            st.success("Análise concluída com sucesso!", icon="🎉")
            
            st.subheader(f"Análise para: {dados_redacao.get('nome_aluno', 'Aluno')}")
            # (O resto do código para exibir os resultados e o botão de download continua o mesmo)
            st.write(f"**Tema:** {dados_redacao.get('tema_redacao', 'N/A')}")
            st.write(f"**Nota Final Estimada:** {dados_redacao.get('nota_final', 'N/A')}")
            
            with st.expander("Ver Comentários Gerais"):
                st.markdown(dados_redacao.get('comentarios_gerais', ''))

            arquivo_docx_bytes = gerador_docx.preencher_e_gerar_docx(dados_redacao, 'template.docx')
            
            if arquivo_docx_bytes:
                nome_aluno_formatado = dados_redacao.get('nome_aluno', 'Aluno').replace(' ', '_')
                nome_arquivo_final = f"Correcao_{nome_aluno_formatado}.docx"
                
                st.download_button(
                    label=f"📥 Baixar Relatório Completo (.docx)",
                    data=arquivo_docx_bytes,
                    file_name=nome_arquivo_final,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            else:
                st.error("Ocorreu um erro ao gerar o arquivo .docx.")
        else:
            st.error("Não foi possível analisar a redação. Verifique a qualidade da imagem ou a resposta da IA no terminal.")