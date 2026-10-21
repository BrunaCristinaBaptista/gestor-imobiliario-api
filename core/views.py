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
    """
    Endereços dos imóveis.

    Não é possível excluir um endereço que tenha imóveis vinculados.
    """

    queryset = Endereco.objects.all()
    serializer_class = EnderecoSerializer
    filterset_class = EnderecoFilter
    search_fields = ("rua", "bairro", "cidade", "cep")
    ordering_fields = ("id", "cidade", "bairro", "rua")
    ordering = ("id",)


class ImovelViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    """
    Imóveis (casa, prédio de kitnets...). Cada imóvel fica num endereço e é dividido em unidades.

    Não é possível excluir um imóvel que tenha despesas vinculadas.
    """

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
    """
    Unidades alugáveis de um imóvel (Kitnet 01, Casa Principal...).

    O campo `status_atual` é calculado: Manutenção, Ocupada (contrato ativo cobrindo
    a data de hoje) ou Disponível. Não é possível excluir uma unidade com contratos.
    """

    queryset = Unidade.objects.all()
    serializer_class = UnidadeSerializer
    filterset_class = UnidadeFilter
    search_fields = ("identificacao", "imovel__nome_imovel")
    ordering_fields = ("id", "identificacao", "imovel__nome_imovel")
    ordering = ("id",)


class InquilinoViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    """
    Inquilinos. O CPF é validado (dígitos verificadores), único e gravado formatado.

    Não é possível excluir um inquilino que tenha contratos.
    """

    queryset = Inquilino.objects.all()
    serializer_class = InquilinoSerializer
    search_fields = ("nome", "sobrenome", "cpf", "email", "telefone")
    ordering_fields = ("id", "nome", "sobrenome")
    ordering = ("id",)


class ContratoViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    """
    Contratos de locação de uma unidade para um inquilino.

    Regra de negócio: uma unidade não pode ter dois contratos ativos com períodos
    sobrepostos, e uma unidade em manutenção não recebe contrato novo.
    Status: 1 = Ativo, 2 = Encerrado, 3 = Rescindido.
    """

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
    """
    Pagamentos mensais de aluguel de um contrato (um por mês de referência, AAAA-MM).

    O campo `status_atual` é calculado: Pago, Atrasado ou Pendente.
    Use `em_aberto=true` para listar os pagamentos ainda não recebidos.
    """

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
    """
    Despesas dos imóveis (IPTU, taxa de lixo, condomínio, manutenção...), com boleto e
    comprovante opcionais (PDF, PNG ou JPG, até 5 MB, enviados como multipart/form-data).

    O campo `status_atual` é calculado: Paga, Atrasada ou Em aberto.
    Use `em_aberto=true` para listar os boletos ainda não pagos.
    """

    queryset = Despesa.objects.all()
    serializer_class = DespesaSerializer
    filterset_class = DespesaFilter
    search_fields = ("descricao", "imovel__nome_imovel", "unidade__identificacao")
    ordering_fields = ("id", "data_vencimento", "valor", "categoria", "descricao")
    ordering = ("id",)
