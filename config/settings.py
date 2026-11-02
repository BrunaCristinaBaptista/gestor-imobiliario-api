"""
Configurações do projeto gestor-imobiliario-api.

Valores sensíveis e o que muda entre o computador e a publicação vêm de variáveis
de ambiente: no computador, do arquivo .env (não versionado, modelo em .env_exemplo);
no Render, das "Environment Variables" do serviço.
"""

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Endereços HTTPS que podem enviar formulários (ex.: login do Admin publicado).
# Ex.: CSRF_TRUSTED_ORIGINS=https://gestor-imobiliario-api.onrender.com
CSRF_TRUSTED_ORIGINS = [
    origem for origem in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origem
]

# No Render, o HTTPS termina no proxy; este cabeçalho avisa o Django que a requisição era HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cloudinary guarda boletos e comprovantes na publicação (o disco do Render é apagado
# a cada reinício). Só é usado quando a variável CLOUDINARY_URL existe.
USAR_CLOUDINARY = bool(os.getenv("CLOUDINARY_URL"))


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    *(["cloudinary_storage", "cloudinary"] if USAR_CLOUDINARY else []),
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serve os arquivos estáticos (CSS do Admin, da API navegável) na publicação.
    "whitenoise.middleware.WhiteNoiseMiddleware",
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


# Sem a variável DATABASE_URL, usa o SQLite local. Com ela (publicação), usa o
# PostgreSQL do Supabase. Ex.: DATABASE_URL=postgresql://usuario:senha@host:5432/postgres
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
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
STATIC_ROOT = BASE_DIR / "staticfiles"  # destino do collectstatic na publicação


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
    # Mensagem do 404 em português (core/excecoes.py)
    "EXCEPTION_HANDLER": "core.excecoes.tratar_excecao",
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
    # Versão fixa do Redoc: a "latest" passou a usar import.meta e deixou a página em branco.
    "REDOC_DIST": "https://cdn.jsdelivr.net/npm/redoc@2.1.5",
}

# Arquivos enviados pelo usuário (boletos e comprovantes)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    # No computador, os arquivos ficam na pasta media/; na publicação, no Cloudinary.
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
            if USAR_CLOUDINARY
            else "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# Permite que o front-end Vue (outra origem, ex.: http://localhost:5173) consuma a API
CORS_ALLOW_ALL_ORIGINS = True
