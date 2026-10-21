"""
Configurações do projeto gestor-imobiliario-api.

Valores sensíveis (SECRET_KEY, DEBUG, ALLOWED_HOSTS) vêm do arquivo .env,
que não é versionado. Use o .env_exemplo como modelo.
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"


REST_FRAMEWORK = {
    # Documentação OpenAPI (Aula 21)
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Filtros (Aula 23), busca e ordenação (Aula 24) valem para todas as ViewSets.
    # Cada ViewSet define seus campos com filterset_class, search_fields e ordering_fields.
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Paginação (Aula 25)
    "DEFAULT_PAGINATION_CLASS": "core.pagination.PaginacaoPadrao",
    "PAGE_SIZE": 10,
    # Autenticação (tutorial, seção 13): token JWT para o front-end e clientes HTTP;
    # sessão para continuar usando a interface navegável do DRF depois de entrar pelo Admin.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Autorização (tutorial, seção 12.3): todos os recursos exigem usuário autenticado.
    # Ficam públicos só o login (/api/token/) e a documentação (/api/docs/, /api/redoc/, /api/schema/).
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# Tempo de vida dos tokens (tutorial, apêndice A7)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=180),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Gestor Imobiliário API",
    "DESCRIPTION": (
        "API REST para gerenciar imóveis próprios: endereços, imóveis, unidades, "
        "inquilinos, contratos de locação, pagamentos de aluguel e despesas. "
        "Regra de negócio principal: uma unidade não pode ter dois contratos ativos "
        "com períodos sobrepostos, e o status de ocupação é calculado a partir dos contratos.\n\n"
        "Autenticação: faça POST em /api/token/ com username e password, copie o campo access "
        "e informe-o no botão Authorize. Sem token, os recursos respondem 401."
    ),
    "VERSION": "1.0.0",
    # Mantém o token informado no Authorize mesmo ao recarregar a página do Swagger.
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
}

# Arquivos enviados pelo usuário (boletos e comprovantes)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# Permite que o front-end Vue (outra origem, ex.: http://localhost:5173) consuma a API
CORS_ALLOW_ALL_ORIGINS = True
