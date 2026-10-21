from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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


class ImovelViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer


class UnidadeViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    queryset = Unidade.objects.all()
    serializer_class = UnidadeSerializer


class InquilinoViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    queryset = Inquilino.objects.all()
    serializer_class = InquilinoSerializer


class ContratoViewSet(ExclusaoProtegidaMixin, ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer


class PagamentoViewSet(ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer


class DespesaViewSet(ModelViewSet):
    queryset = Despesa.objects.all()
    serializer_class = DespesaSerializer
