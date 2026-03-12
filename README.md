# AI Essay Parser

Corretor automatizado de redações manuscritas baseado em visão computacional. Utiliza o modelo **Google Gemini** para interpretar imagens de textos escritos à mão, avaliar as cinco competências do ENEM e gerar relatórios formatados em Word (.docx).

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini-orange)
![Architecture](https://img.shields.io/badge/Architecture-Service%20Layer-purple)
![License](https://img.shields.io/badge/License-Apache%202.0-green)

---

## Funcionalidades

- **Leitura de Manuscritos** — Interpretação de texto manuscrito via visão computacional (Gemini Vision), com tratamento de caligrafia e erros de OCR.
- **Correção Pedagógica (ENEM)** — Avaliação detalhada nas 5 competências oficiais do ENEM (C1 a C5), com notas na escala de 40 pontos e análise textual por competência.
- **Aprendizado Contínuo (OCR)** — Sistema de feedback que permite ao professor corrigir erros de leitura da IA. As correções são salvas e injetadas automaticamente nos prompts seguintes (Few-Shot Learning).
- **Interface Web (Streamlit)** — Aplicação com 4 abas:
  - Correção Individual (com download em pacote ZIP: DOCX + imagem)
  - Correção em Lote (pasta local)
  - Correção em Lote (Google Drive)
  - Treinamento OCR (revisão lado a lado com formulário de feedback)
- **Relatórios em Word** — Geração automática de `.docx` a partir de template customizável, com preenchimento de notas, análises e dados da turma.
- **Integração com Google Drive** — Upload e download de arquivos para processamento em lote na nuvem.

---

## Estrutura do Projeto

```text
Essay_Parser/
├── src/
│   ├── app/
│   │   ├── core/
│   │   │   ├── logger.py            # Logger padronizado
│   │   │   └── feedback_manager.py  # Gestão de feedback OCR
│   │   ├── services/
│   │   │   ├── ai_service.py        # Integração com Gemini API
│   │   │   ├── drive_service.py     # Integração com Google Drive
│   │   │   └── report_service.py    # Geração de relatórios DOCX
│   │   └── main.py                  # Interface Web (Streamlit)
│   └── config.py                    # Configurações centralizadas
├── assets/
│   ├── prompt.txt                   # Prompt do sistema (critérios ENEM)
│   └── template.docx               # Template do relatório Word
├── data/
│   └── feedback_ocr.json           # Histórico de correções de leitura
├── secrets/                         # Chaves de API e tokens (git ignored)
├── .env                             # Variáveis de ambiente
├── .env.example                     # Modelo de configuração
├── requirements.txt                 # Dependências Python
├── run.sh                           # Script de inicialização
└── LICENSE
```

---

## Instalacao e Configuracao

### Pre-requisitos

- Python 3.10 ou superior
- Chave de API do Google Gemini ([console.cloud.google.com](https://console.cloud.google.com))
- (Opcional) Credenciais OAuth para integração com Google Drive

### 1. Clonar e instalar dependencias

```bash
git clone git@github.com:claudio1code/Essay_Parser.git
cd Essay_Parser

python -m venv venv
source venv/bin/activate     # Linux/Mac
# venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 2. Configurar variaveis de ambiente

Copie o arquivo de exemplo e edite com seus dados:

```bash
cp .env.example .env
```

Variaveis principais:

| Variavel | Descricao | Exemplo |
|---|---|---|
| `GEMINI_API_KEY` | Chave de API do Google Gemini | `AIzaSy...` |
| `GEMINI_MODEL_NAME` | Modelo a utilizar | `gemini-2.0-flash` |
| `GOOGLE_CREDENTIALS_FILE` | Arquivo de Service Account (opcional) | `google-credentials.json` |
| `DRIVE_CREDENTIALS_FILE` | Arquivo OAuth do Drive (opcional) | `credentials.json` |
| `DRIVE_FOLDER_INPUT_ID` | ID da pasta de entrada no Drive | `1c_8ybb...` |
| `DRIVE_FOLDER_OUTPUT_ID` | ID da pasta de saida no Drive | `16xRIP...` |

### 3. Configurar credenciais (opcional, para Google Drive)

1. Coloque os arquivos de credenciais na pasta `secrets/`.
2. O token OAuth sera gerado automaticamente no primeiro uso do modo Drive.

---

## Como Usar

Inicie a aplicacao com o script fornecido:

```bash
./run.sh
```

Ou manualmente:

```bash
source venv/bin/activate
PYTHONPATH=./src streamlit run src/app/main.py
```

A interface web abrira em `http://localhost:8501` com as seguintes abas:

### Correcao Individual

1. Faca upload de uma foto da redacao (JPG/PNG).
2. Clique em **Analisar Redacao**.
3. Visualize a imagem ao lado do resultado (nome, nota, competencias).
4. Baixe o pacote ZIP contendo o relatorio `.docx` e a imagem original.

### Correcao em Lote (Local)

1. Informe o caminho da pasta com as imagens.
2. Informe o caminho da pasta de saida para os relatorios.
3. Clique em **Iniciar Processamento em Lote**.

### Correcao em Lote (Google Drive)

1. Cole os links das pastas de entrada e saida do Drive.
2. Clique em **Iniciar Processamento Cloud**.

### Treinamento OCR

1. Apos corrigir uma redacao na aba Individual, va para esta aba.
2. Compare a imagem original com os comentarios e analises gerados.
3. Se identificar um erro de leitura (ex: "Datapolha" no lugar de "Datafolha"), preencha o formulario e salve.
4. A correcao sera usada automaticamente nas proximas analises.

---

## Personalizacao

| Item | Arquivo | Descricao |
|---|---|---|
| Criterios de correcao | `assets/prompt.txt` | Prompt com a grade ENEM e instrucoes pedagogicas |
| Layout do relatorio | `assets/template.docx` | Template Word com placeholders (`{{NOME_ALUNO}}`, `{{NOTA_C1}}`, etc.) |

---

## Tecnologias

| Tecnologia | Uso |
|---|---|
| [Streamlit](https://streamlit.io) | Interface web |
| [Google Gemini API](https://ai.google.dev) | Analise de imagem e texto via IA |
| [python-docx](https://python-docx.readthedocs.io) | Geracao de relatorios Word |
| [Pillow](https://python-pillow.org) | Manipulacao de imagens |
| [Google Drive API](https://developers.google.com/drive) | Integracao com armazenamento em nuvem |

---

## Desenvolvimento

Este projeto foi desenvolvido com auxilio de ferramentas de IA generativa para aceleracao de codigo, refatoracao e documentacao. A arquitetura do sistema, os criterios pedagogicos, o design de prompt baseado nas diretrizes oficiais do MEC/INEP e as decisoes de produto sao de autoria do desenvolvedor.

---

## Licenca

Distribuido sob a licenca **Apache 2.0**. Consulte o arquivo [LICENSE](LICENSE) para detalhes.
