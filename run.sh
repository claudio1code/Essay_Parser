#!/bin/bash
#
# Este script inicia a aplicação Streamlit, configurando o PYTHONPATH
# para que o Python encontre os módulos dentro da pasta 'src'.

echo "🚀 Iniciando o Corretor de Redação AI..."

# Ativa o ambiente virtual e executa o Streamlit
source venv/bin/activate && PYTHONPATH=./src ./venv/bin/python -m streamlit run src/app/main.py
