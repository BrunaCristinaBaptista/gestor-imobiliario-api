# Gestor Imobiliário — API REST

Projeto final da disciplina **Desenvolvimento Web II** (BSI4 — IFC Araquari).

API REST para uma pessoa gerenciar os próprios imóveis: endereços, imóveis, unidades, inquilinos, contratos de locação, aluguéis recebidos e despesas (IPTU, taxa de lixo, condomínio etc.).

- **Back-end:** Django + Django REST Framework
- **Front-end:** Vue 3 — repositório [gestor-imobiliario-vue](https://github.com/BrunaCristinaBaptista/gestor-imobiliario-vue)
- **Autora:** Bruna Cristina Baptista (trabalho individual)

---

## Sumário

- [Gestor Imobiliário — API REST](#gestor-imobiliário--api-rest)
  - [Sumário](#sumário)
  - [1. Como executar](#1-como-executar)
  - [2. Domínio e entidades](#2-domínio-e-entidades)
  - [3. Regras de negócio](#3-regras-de-negócio)
  - [4. Documentação da API](#4-documentação-da-api)
  - [5. Construção passo a passo](#5-construção-passo-a-passo)
    - [Etapa 1 — Criação do projeto (Aula 17)](#etapa-1--criação-do-projeto-aula-17)
  - [6. Checklist da Parte 8](#6-checklist-da-parte-8)

---

## 1. Como executar

Pré-requisitos: [uv](https://docs.astral.sh/uv/) e Git.

```bash
git clone https://github.com/BrunaCristinaBaptista/gestor-imobiliario-api
cd gestor-imobiliario-api
uv sync
cp .env_exemplo .env
```

Gere uma chave secreta e cole no campo `SECRET_KEY` do arquivo `.env`:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Crie o banco, um usuário administrador e suba o servidor:

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

| Recurso | URL |
|---|---|
| Django Admin | http://127.0.0.1:8000/admin/ |
| API | http://127.0.0.1:8000/api/ *(Etapa 3)* |
| Swagger | http://127.0.0.1:8000/api/docs/ *(Etapa 6)* |

---

## 2. Domínio e entidades

*Preenchido na Etapa 2.*

## 3. Regras de negócio

*Preenchido na Etapa 4.*

## 4. Documentação da API

*Preenchido nas Etapas 3 a 6.*

---

## 5. Construção passo a passo

O projeto foi construído seguindo a Parte 7 do material da disciplina (Aulas 17 a 26), com o tutorial `django-drf-tutorial` como apoio para o que o material não cobre (vários models relacionados, frontend, autenticação).

### Etapa 1 — Criação do projeto (Aula 17)

**Objetivo:** criar o projeto Django com o `uv`, separar a configuração global (`config`) da aplicação do domínio (`core`) e manter a chave secreta fora do repositório.

**1.1 Criar a pasta e o ambiente com uv**

```bash
mkdir gestor-imobiliario-api
cd gestor-imobiliario-api
uv init --app --python 3.14 --no-workspace .
rm -f main.py
uv add django python-dotenv
```

- `uv init --app` cria o `pyproject.toml` (lista de dependências do projeto).
- `uv add` instala o pacote e registra a versão exata no `uv.lock`. Quem clonar o projeto instala as mesmas versões com `uv sync`.
- `python-dotenv` lê o arquivo `.env`, onde fica a chave secreta.

**1.2 Criar o projeto `config` e a aplicação `core`**

```bash
uv run django-admin startproject config .
uv run python manage.py startapp core
```

- **Projeto (`config/`)**: configurações globais (`settings.py`) e roteamento principal (`urls.py`).
- **Aplicação (`core/`)**: o módulo do domínio imobiliário — models, serializers, views e admin.
- O `.` no final cria o projeto na pasta atual, sem criar uma subpasta extra.

**1.3 Registrar a aplicação e ajustar idioma e fuso horário**

Em `config/settings.py`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
```

**1.4 Tirar a chave secreta do código**

O `startproject` grava uma `SECRET_KEY` dentro do `settings.py`. Se ela for para o GitHub, fica pública para sempre. Por isso ela passa a ser lida do arquivo `.env`, que não é versionado.

No início de `config/settings.py`:

```python
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
```

> `DEBUG` é comparado com `"True"` porque `os.getenv` sempre devolve texto, e o texto `"False"` seria considerado verdadeiro pelo Python.

Arquivo `.env_exemplo` (versionado, sem segredos):

```ini
SECRET_KEY=troque-por-uma-chave-gerada
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Criar o `.env` real a partir dele:

```bash
cp .env_exemplo .env
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**1.5 Arquivo `.gitignore`**

```gitignore
.venv/
__pycache__/
*.py[cod]
db.sqlite3
db.sqlite3-journal
media/
.env
.vscode/
.idea/
```

**1.6 Executar**

```bash
uv run python manage.py runserver
```

Ao acessar http://127.0.0.1:8000/, a página inicial do Django confirma que o projeto funciona. Ainda não há models nem API.

**Estrutura ao final da etapa**

```text
gestor-imobiliario-api/
├── .env_exemplo
├── .gitignore
├── .python-version
├── manage.py
├── pyproject.toml
├── uv.lock
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── core/
    ├── admin.py
    ├── models.py
    ├── views.py
    └── migrations/
```

**Commit**

```bash
git add .
git commit -m "feat(django): cria projeto inicial"
```

---

## 6. Checklist da Parte 8

**Obrigatório**

- [x] Escolhi um domínio próprio, diferente da simples reprodução da API de Produtos.
- [ ] Implementei `GET` da coleção, `GET` individual, `POST`, `PUT` e `DELETE`.
- [ ] Utilizei códigos HTTP adequados e respostas em JSON quando aplicável.
- [ ] Os dados estão persistidos em um banco de dados.
- [ ] Defini e implementei validações no backend.
- [ ] Implementei pelo menos uma regra de negócio além do CRUD.
- [ ] Implementei filtro, busca textual, ordenação e paginação.
- [ ] Documentei a API e as instruções de execução.
- [x] Versionei o código em um repositório Git.
- [ ] Informei todas as URLs necessárias para avaliação.
- [ ] Preparei a demonstração e a explicação do projeto para a apresentação obrigatória.
- [ ] Realizei a entrega pelo SIGAA, enviando o link do repositório GitHub do projeto.
- [ ] Estou preparado para apresentar o projeto em sala de aula, para toda a turma, após a data de entrega.
- [ ] Testei a aplicação após instalar e configurar o projeto seguindo o `README`.

**Opcional**

- [ ] Publiquei a aplicação.
- [ ] Criei um frontend integrado à API.
- [ ] Implementei 3 ou mais models/tabelas relevantes para o domínio.
- [ ] Implementei e testei login, autenticação e acesso a pelo menos um recurso protegido.
- [x] Removi do repositório credenciais, senhas e chaves privadas.
