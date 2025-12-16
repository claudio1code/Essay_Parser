# ✍️ Automated Essay Grader (Corretor de Redações com IA)

> Uma ferramenta de automação que utiliza Visão Computacional e LLMs (Google Gemini 1.5) para corrigir redações manuscritas com base nos critérios oficiais do ENEM, gerando relatórios detalhados em PDF/Docx.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini%201.5-orange)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Sobre o Projeto

Este projeto foi desenvolvido para resolver o gargalo na correção de redações escolares. Diferente de corretores gramaticais comuns, este sistema é capaz de:

1.  **Ler manuscritos:** Aceita fotos de folhas de redação (JPG/PNG).
2.  **Análise Pedagógica:** Avalia as 5 competências oficiais do ENEM (Norma Culta, Compreensão do Tema, Argumentação, Coesão, Proposta de Intervenção).
3.  **Relatórios Automatizados:** Gera um arquivo `.docx` formatado com a nota e comentários detalhados.
4.  **Modo Batch (Lote):** Possui um módulo de automação (`corrigir_em_lote.py`) que monitora uma pasta no Google Drive, corrige novas redações automaticamente e salva os relatórios em uma pasta de saída.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Inteligência Artificial:** Google Gemini 1.5 Flash (Multimodal Vision + Text)
* **Interface:** Streamlit
* **Automação de Documentos:** Python-docx
* **Integração em Nuvem:** Google Drive API v3

## 🚀 Como Executar

### Pré-requisitos
* Python 3.10 ou superior
* Chave de API do Google Gemini (AI Studio)
* Credenciais do Google Cloud (para o módulo de Drive)

### Instalação

1. Clone o repositório:
   ```bash
   git clone [https://github.com/claudio1code/automated-essay-grader.git](https://github.com/claudio1code/automated-essay-grader.git)
   cd automated-essay-grader

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt

3. Configure as variáveis de ambiente: Crie um arquivo .env na raiz do projeto:
   ```bash
   GOOGLE_API_KEY="Sua_Chave_Gemini_Aqui"
Para o módulo de Drive, adicione o arquivo credentials.json e google-credentials.json (Service Account) na raiz.

**Rodando a Aplicação Web
Para utilizar a interface visual de correção individual:




   
