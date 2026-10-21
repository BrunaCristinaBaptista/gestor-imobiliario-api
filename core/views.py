from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import (
    ContratoFilter,
    DespesaFilter,
    EnderecoFilter,
    ImovelFilter,
    PagamentoFilter,
    UnidadeFilter,
)
from .models import Contrato, Despesa, Endereco, Imovel, Inquilino, Pagamento, Unidade
from .serializers import (
    ContratoSerializer,
    DespesaSerializer,
    EnderecoSerializer,
    ImovelSerializer,
    InquilinoSerializer,
    PagamentoSerializer,
    UnidadeSerializer,
)


class ExclusaoProtegidaMixin:
    """
    Os models usam on_delete=PROTECT para preservar o histórico. Sem este tratamento,
    excluir um registro que ainda é usado por outro gera erro 500. Aqui o erro vira
    uma resposta 400 com a mensagem no formato { "detail": ... }.
    """

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "detail": "Não é possível excluir este registro porque "
                    "existem outros registros vinculados a ele."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class EnderecoViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    queryset = Endereco.objects.all()
    serializer_class = EnderecoSerializer
    filterset_class = EnderecoFilter
    search_fields = ("rua", "bairro", "cidade", "cep")
    ordering_fields = ("id", "cidade", "bairro", "rua")
    ordering = ("id",)


class ImovelViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    filterset_class = ImovelFilter
    search_fields = (
        "nome_imovel",
        "tipo_imovel",
        "endereco__rua",
        "endereco__bairro",
        "endereco__cidade",
    )
    ordering_fields = ("id", "nome_imovel", "tipo_imovel")
    ordering = ("id",)


class UnidadeViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    queryset = Unidade.objects.all()
    serializer_class = UnidadeSerializer
    filterset_class = UnidadeFilter
    search_fields = ("identificacao", "imovel__nome_imovel")
    ordering_fields = ("id", "identificacao", "imovel__nome_imovel")
    ordering = ("id",)


class InquilinoViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    queryset = Inquilino.objects.all()
    serializer_class = InquilinoSerializer
    search_fields = ("nome", "sobrenome", "cpf", "email", "telefone")
    ordering_fields = ("id", "nome", "sobrenome")
    ordering = ("id",)


class ContratoViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    filterset_class = ContratoFilter
    search_fields = (
        "inquilino__nome",
        "inquilino__sobrenome",
        "unidade__identificacao",
        "unidade__imovel__nome_imovel",
    )
    ordering_fields = ("id", "data_inicio", "data_termino", "valor_aluguel", "status")
    ordering = ("id",)


class PagamentoViewSet(ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    filterset_class = PagamentoFilter
    search_fields = (
        "mes_referencia",
        "contrato__inquilino__nome",
        "contrato__inquilino__sobrenome",
        "contrato__unidade__identificacao",
    )
    ordering_fields = (
        "id",
        "mes_referencia",
        "data_vencimento",
        "data_pagamento",
        "valor_previsto",
    )
    ordering = ("id",)


class DespesaViewSet(ModelViewSet):
    queryset = Despesa.objects.all()
    serializer_class = DespesaSerializer
    filterset_class = DespesaFilter
    search_fields = ("descricao", "imovel__nome_imovel", "unidade__identificacao")
    ordering_fields = ("id", "data_vencimento", "valor", "categoria", "descricao")
    ordering = ("id",)
