import re
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Contrato, Despesa, Endereco, Imovel, Inquilino, Pagamento, Unidade

# Padrão usado em todos os serializers:
# - a chave estrangeira (ex.: "unidade") recebe e devolve o id, para criar e editar;
# - o campo "<nome>_descricao" é só leitura e mostra o texto do __str__ do registro
#   relacionado, para quem consome a API não ver apenas um número;
# - validate_<campo> valida um campo; validate valida regras que envolvem vários campos.

UFS = (
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
    "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
)
EXTENSOES_PERMITIDAS = (".pdf", ".png", ".jpg", ".jpeg")
TAMANHO_MAXIMO_ARQUIVO = 5 * 1024 * 1024  # 5 MB


def somente_digitos(valor):
    return re.sub(r"\D", "", valor)


def validar_texto_minimo(valor, minimo=2):
    texto = valor.strip()
    if len(texto) < minimo:
        raise serializers.ValidationError(
            f"Informe pelo menos {minimo} caracteres."
        )
    return texto


def validar_arquivo(arquivo):
    if arquivo is None:
        return arquivo
    if not arquivo.name.lower().endswith(EXTENSOES_PERMITIDAS):
        raise serializers.ValidationError("Envie um arquivo PDF, PNG ou JPG.")
    if arquivo.size > TAMANHO_MAXIMO_ARQUIVO:
        raise serializers.ValidationError("O arquivo não pode passar de 5 MB.")
    return arquivo


def validar_data_pagamento(data):
    if data is not None and data > timezone.localdate():
        raise serializers.ValidationError("A data de pagamento não pode ser futura.")
    return data


def cpf_valido(digitos):
    if len(digitos) != 11 or len(set(digitos)) == 1:
        return False
    numeros = [int(d) for d in digitos]
    for posicao in (9, 10):
        soma = sum(numeros[i] * (posicao + 1 - i) for i in range(posicao))
        digito = (soma * 10) % 11 % 10
        if digito != numeros[posicao]:
            return False
    return True


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ("id", "cep", "estado", "cidade", "bairro", "rua", "numero")

    def validate_cep(self, value):
        digitos = somente_digitos(value)
        if len(digitos) != 8:
            raise serializers.ValidationError("O CEP deve ter 8 dígitos.")
        return f"{digitos[:5]}-{digitos[5:]}"

    def validate_estado(self, value):
        uf = value.strip().upper()
        if uf not in UFS:
            raise serializers.ValidationError("Informe a sigla de um estado válido (ex.: SC).")
        return uf

    def validate_cidade(self, value):
        return validar_texto_minimo(value)

    def validate_bairro(self, value):
        return validar_texto_minimo(value)

    def validate_rua(self, value):
        return validar_texto_minimo(value)


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

    def validate_nome_imovel(self, value):
        return validar_texto_minimo(value)

    def validate_tipo_imovel(self, value):
        return validar_texto_minimo(value)


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

    def validate_identificacao(self, value):
        return validar_texto_minimo(value)


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

    def validate_nome(self, value):
        return validar_texto_minimo(value)

    def validate_sobrenome(self, value):
        return validar_texto_minimo(value)

    def validate_cpf(self, value):
        digitos = somente_digitos(value)
        if not cpf_valido(digitos):
            raise serializers.ValidationError("CPF inválido.")
        cpf = f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
        # O CPF é gravado sempre formatado; por isso a unicidade é conferida aqui,
        # depois da formatação ("11144477735" e "111.444.777-35" são o mesmo CPF).
        mesmos_cpfs = Inquilino.objects.filter(cpf=cpf)
        if self.instance is not None:
            mesmos_cpfs = mesmos_cpfs.exclude(pk=self.instance.pk)
        if mesmos_cpfs.exists():
            raise serializers.ValidationError("Já existe um inquilino com este CPF.")
        return cpf

    def validate_telefone(self, value):
        digitos = somente_digitos(value)
        if len(digitos) == 11:
            return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
        if len(digitos) == 10:
            return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
        raise serializers.ValidationError("Informe o telefone com DDD (10 ou 11 dígitos).")


class ContratoSerializer(serializers.ModelSerializer):
    unidade_descricao = serializers.CharField(source="unidade", read_only=True)
    inquilino_descricao = serializers.CharField(source="inquilino", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    quantidade_cobrancas = serializers.IntegerField(source="pagamentos.count", read_only=True)

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
            "quantidade_cobrancas",
        )

    def validate_dia_vencimento(self, value):
        # Até 28, porque todo mês tem pelo menos 28 dias.
        if not 1 <= value <= 28:
            raise serializers.ValidationError("O dia de vencimento deve ser de 1 a 28.")
        return value

    def validate_valor_aluguel(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError("O valor do aluguel deve ser maior que zero.")
        return value

    def validate_valor_caucao(self, value):
        if value < Decimal("0"):
            raise serializers.ValidationError("O valor da caução não pode ser negativo.")
        return value

    def validate_numero_parcelas_caucao(self, value):
        if value < 1:
            raise serializers.ValidationError("O número de parcelas deve ser pelo menos 1.")
        return value

    def validate(self, attrs):
        # Num PATCH só chegam os campos enviados; os demais vêm do contrato atual.
        def valor(campo):
            if campo in attrs:
                return attrs[campo]
            return getattr(self.instance, campo, None)

        unidade = valor("unidade")
        data_inicio = valor("data_inicio")
        data_termino = valor("data_termino")
        status = valor("status")
        if status is None:
            status = Contrato.Status.ATIVO

        if data_termino <= data_inicio:
            raise serializers.ValidationError(
                {"data_termino": "A data de término deve ser posterior à data de início."}
            )

        if status != Contrato.Status.ATIVO:
            return attrs

        # Regra de negócio 1: unidade em manutenção não recebe contrato novo.
        unidade_mudou = self.instance is None or self.instance.unidade_id != unidade.id
        if unidade.em_manutencao and unidade_mudou:
            raise serializers.ValidationError(
                {"unidade": "Esta unidade está em manutenção e não pode receber um novo contrato."}
            )

        # Regra de negócio 2: uma unidade não pode ter dois contratos ativos
        # com períodos que se sobrepõem.
        conflitos = Contrato.objects.filter(
            unidade=unidade,
            status=Contrato.Status.ATIVO,
            data_inicio__lte=data_termino,
            data_termino__gte=data_inicio,
        )
        if self.instance is not None:
            conflitos = conflitos.exclude(pk=self.instance.pk)
        conflito = conflitos.first()
        if conflito:
            raise serializers.ValidationError(
                {
                    "unidade": (
                        f"Esta unidade já tem o contrato #{conflito.id} ativo de "
                        f"{conflito.data_inicio:%d/%m/%Y} a {conflito.data_termino:%d/%m/%Y}, "
                        "que se sobrepõe ao período informado."
                    )
                }
            )
        return attrs

    def create(self, validated_data):
        # Regra de negócio: um contrato criado como ativo já nasce com as cobranças
        # de todos os meses da vigência. O atomic garante que, se algo falhar,
        # nem o contrato nem as cobranças ficam gravados pela metade.
        with transaction.atomic():
            contrato = super().create(validated_data)
            if contrato.status == Contrato.Status.ATIVO:
                contrato.gerar_cobrancas()
        return contrato


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

    def validate_mes_referencia(self, value):
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
            raise serializers.ValidationError("Use o formato AAAA-MM (ex.: 2026-10).")
        return value

    def validate_valor_previsto(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError("O valor previsto deve ser maior que zero.")
        return value

    def validate_valor_pago(self, value):
        if value is not None and value <= Decimal("0"):
            raise serializers.ValidationError("O valor pago deve ser maior que zero.")
        return value

    def validate_data_pagamento(self, value):
        return validar_data_pagamento(value)

    def validate_comprovante(self, value):
        return validar_arquivo(value)

    def validate(self, attrs):
        def valor(campo):
            if campo in attrs:
                return attrs[campo]
            return getattr(self.instance, campo, None)

        contrato = valor("contrato")
        mes_referencia = valor("mes_referencia")
        data_pagamento = valor("data_pagamento")
        valor_pago = valor("valor_pago")

        # O mês cobrado precisa estar dentro da vigência do contrato.
        ano, mes = (int(parte) for parte in mes_referencia.split("-"))
        inicio = (contrato.data_inicio.year, contrato.data_inicio.month)
        termino = (contrato.data_termino.year, contrato.data_termino.month)
        if not inicio <= (ano, mes) <= termino:
            raise serializers.ValidationError(
                {
                    "mes_referencia": (
                        f"O mês está fora da vigência do contrato "
                        f"({contrato.data_inicio:%m/%Y} a {contrato.data_termino:%m/%Y})."
                    )
                }
            )

        # Pagamento registrado precisa ter data e valor juntos.
        if (data_pagamento is None) != (valor_pago is None):
            raise serializers.ValidationError(
                {"valor_pago": "Informe a data de pagamento e o valor pago juntos."}
            )
        return attrs


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

    def validate_descricao(self, value):
        return validar_texto_minimo(value, minimo=3)

    def validate_valor(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError("O valor deve ser maior que zero.")
        return value

    def validate_data_pagamento(self, value):
        return validar_data_pagamento(value)

    def validate_boleto(self, value):
        return validar_arquivo(value)

    def validate_comprovante(self, value):
        return validar_arquivo(value)

    def validate(self, attrs):
        imovel = attrs.get("imovel", getattr(self.instance, "imovel", None))
        unidade = attrs.get("unidade", getattr(self.instance, "unidade", None))
        if unidade is not None and unidade.imovel_id != imovel.id:
            raise serializers.ValidationError(
                {"unidade": "Esta unidade não pertence ao imóvel informado."}
            )
        return attrs
