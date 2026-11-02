#!/usr/bin/env bash
# Script de build do Render (Build Command: ./build.sh)
# Sai do script se algum comando falhar
set -o errexit

# O uv instala o Python dentro da pasta do projeto, para ele continuar
# disponível quando o serviço for iniciado (fora da pasta, ele se perderia).
export UV_PYTHON_INSTALL_DIR="$PWD/.uv-python"

# Instala o uv e as dependências exatas do uv.lock
pip install uv
uv sync --frozen

# Coleta os arquivos estáticos (CSS do Admin e da API navegável)
uv run python manage.py collectstatic --no-input

# Aplica as migrações no banco do Supabase
uv run python manage.py migrate
