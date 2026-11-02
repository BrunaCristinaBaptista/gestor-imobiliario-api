from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.views import exception_handler


def tratar_excecao(exc, context):
    """
    Tratamento de erros da API, ligado em REST_FRAMEWORK["EXCEPTION_HANDLER"].

    Quando um id não existe, o Django gera a mensagem fixa em inglês
    "No <Model> matches the given query.", que não passa pela tradução.
    Aqui ela vira uma mensagem em português. Os demais erros seguem o
    tratamento padrão do DRF.
    """
    if isinstance(exc, Http404):
        exc = NotFound("Registro não encontrado.")
    return exception_handler(exc, context)
