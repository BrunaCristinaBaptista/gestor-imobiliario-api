from django_filters import rest_framework as filters

from .models import Contrato, Despesa, Endereco, Imovel, Pagamento, Unidade

# Filtros estruturados (Aula 23): cada parâmetro da URL vira uma condição no banco.
# lookup_expr define a comparação: exact (igual), iexact (igual sem diferenciar
# maiúsculas), gte (maior ou igual), lte (menor ou igual), isnull (é nulo).


class EnderecoFilter(filters.FilterSet):
    estado = filters.CharFilter(field_name="estado", lookup_expr="iexact")
    cidade = filters.CharFilter(field_name="cidade", lookup_expr="iexact")

    class Meta:
        model = Endereco
        fields = ("estado", "cidade")


class ImovelFilter(filters.FilterSet):
    tipo_imovel = filters.CharFilter(field_name="tipo_imovel", lookup_expr="iexact")
    cidade = filters.CharFilter(field_name="endereco__cidade", lookup_expr="iexact")

    class Meta:
        model = Imovel
        fields = ("tipo_imovel", "cidade", "endereco")


class UnidadeFilter(filters.FilterSet):
    class Meta:
        model = Unidade
        fields = ("imovel", "em_manutencao")


class ContratoFilter(filters.FilterSet):
    imovel = filters.NumberFilter(field_name="unidade__imovel")
    valor_minimo = filters.NumberFilter(field_name="valor_aluguel", lookup_expr="gte")
    valor_maximo = filters.NumberFilter(field_name="valor_aluguel", lookup_expr="lte")

    class Meta:
        model = Contrato
        fields = ("status", "unidade", "inquilino", "imovel", "valor_minimo", "valor_maximo")


class PagamentoFilter(filters.FilterSet):
    em_aberto = filters.BooleanFilter(field_name="data_pagamento", lookup_expr="isnull")
    vencimento_minimo = filters.DateFilter(field_name="data_vencimento", lookup_expr="gte")
    vencimento_maximo = filters.DateFilter(field_name="data_vencimento", lookup_expr="lte")

    class Meta:
        model = Pagamento
        fields = (
            "contrato",
            "mes_referencia",
            "em_aberto",
            "vencimento_minimo",
            "vencimento_maximo",
        )


class DespesaFilter(filters.FilterSet):
    em_aberto = filters.BooleanFilter(field_name="data_pagamento", lookup_expr="isnull")
    valor_minimo = filters.NumberFilter(field_name="valor", lookup_expr="gte")
    valor_maximo = filters.NumberFilter(field_name="valor", lookup_expr="lte")
    vencimento_minimo = filters.DateFilter(field_name="data_vencimento", lookup_expr="gte")
    vencimento_maximo = filters.DateFilter(field_name="data_vencimento", lookup_expr="lte")

    class Meta:
        model = Despesa
        fields = (
            "imovel",
            "unidade",
            "categoria",
            "em_aberto",
            "valor_minimo",
            "valor_maximo",
            "vencimento_minimo",
            "vencimento_maximo",
        )
