from rest_framework import serializers

from .models import Contrato, Despesa, Endereco, Imovel, Inquilino, Pagamento, Unidade

# Padrão usado em todos os serializers:
# - a chave estrangeira (ex.: "unidade") recebe e devolve o id, para criar e editar;
# - o campo "<nome>_descricao" é só leitura e mostra o texto do __str__ do registro
#   relacionado, para quem consome a API não ver apenas um número.


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ("id", "cep", "estado", "cidade", "bairro", "rua", "numero")


class ImovelSerializer(serializers.ModelSerializer):
    endereco_descricao = serializers.CharField(source="endereco", read_only=True)

    class Meta:
        model = Imovel
        fields = (
            "id",
            "nome_imovel",
            "tipo_imovel",
            "foto_imovel",
            "endereco",
            "endereco_descricao",
        )


class UnidadeSerializer(serializers.ModelSerializer):
    imovel_descricao = serializers.CharField(source="imovel", read_only=True)
    status_atual = serializers.CharField(read_only=True)

    class Meta:
        model = Unidade
        fields = (
            "id",
            "imovel",
            "imovel_descricao",
            "identificacao",
            "em_manutencao",
            "status_atual",
        )


class InquilinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquilino
        fields = (
            "id",
            "nome",
            "sobrenome",
            "cpf",
            "estado_civil",
            "profissao",
            "telefone",
            "email",
        )


class ContratoSerializer(serializers.ModelSerializer):
    unidade_descricao = serializers.CharField(source="unidade", read_only=True)
    inquilino_descricao = serializers.CharField(source="inquilino", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Contrato
        fields = (
            "id",
            "unidade",
            "unidade_descricao",
            "inquilino",
            "inquilino_descricao",
            "data_inicio",
            "data_termino",
            "dia_vencimento",
            "valor_aluguel",
            "valor_caucao",
            "numero_parcelas_caucao",
            "status",
            "status_display",
        )


class PagamentoSerializer(serializers.ModelSerializer):
    contrato_descricao = serializers.CharField(source="contrato", read_only=True)
    status_atual = serializers.CharField(read_only=True)

    class Meta:
        model = Pagamento
        fields = (
            "id",
            "contrato",
            "contrato_descricao",
            "mes_referencia",
            "data_vencimento",
            "data_pagamento",
            "valor_previsto",
            "valor_pago",
            "comprovante",
            "status_atual",
        )


class DespesaSerializer(serializers.ModelSerializer):
    imovel_descricao = serializers.CharField(source="imovel", read_only=True)
    unidade_descricao = serializers.CharField(source="unidade", read_only=True)
    categoria_display = serializers.CharField(
        source="get_categoria_display", read_only=True
    )
    status_atual = serializers.CharField(read_only=True)

    class Meta:
        model = Despesa
        fields = (
            "id",
            "imovel",
            "imovel_descricao",
            "unidade",
            "unidade_descricao",
            "descricao",
            "categoria",
            "categoria_display",
            "valor",
            "data_vencimento",
            "data_pagamento",
            "boleto",
            "comprovante",
            "status_atual",
        )
