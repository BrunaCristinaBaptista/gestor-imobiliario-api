from django.db import models
from django.utils import timezone


class Endereco(models.Model):
    cep = models.CharField(max_length=9)
    estado = models.CharField(max_length=2)
    cidade = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    rua = models.CharField(max_length=150)
    numero = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.bairro}, {self.cidade}/{self.estado}"


class Imovel(models.Model):
    endereco = models.ForeignKey(
        Endereco, on_delete=models.PROTECT, related_name="imoveis"
    )
    nome_imovel = models.CharField(max_length=100)
    tipo_imovel = models.CharField(max_length=50)
    foto_imovel = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Imóvel"
        verbose_name_plural = "Imóveis"

    def __str__(self):
        return self.nome_imovel


class Unidade(models.Model):
    imovel = models.ForeignKey(
        Imovel, on_delete=models.CASCADE, related_name="unidades"
    )
    identificacao = models.CharField(max_length=50)
    em_manutencao = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Unidade"
        verbose_name_plural = "Unidades"
        constraints = (
            models.UniqueConstraint(
                fields=["imovel", "identificacao"],
                name="unique_unidade_por_imovel",
            ),
        )

    def __str__(self):
        return f"{self.imovel.nome_imovel} - {self.identificacao}"

    @property
    def status_atual(self):
        # Regra de negócio: o status não é gravado; é calculado a cada consulta.
        if self.em_manutencao:
            return "Manutenção"
        hoje = timezone.localdate()
        tem_contrato_vigente = self.contratos.filter(
            status=Contrato.Status.ATIVO,
            data_inicio__lte=hoje,
            data_termino__gte=hoje,
        ).exists()
        if tem_contrato_vigente:
            return "Ocupada"
        return "Disponível"


class Inquilino(models.Model):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    estado_civil = models.CharField(max_length=30, blank=True)
    profissao = models.CharField(max_length=100, blank=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Inquilino"
        verbose_name_plural = "Inquilinos"

    def __str__(self):
        return f"{self.nome} {self.sobrenome}"


class Contrato(models.Model):
    class Status(models.IntegerChoices):
        ATIVO = 1, "Ativo"
        ENCERRADO = 2, "Encerrado"
        RESCINDIDO = 3, "Rescindido"

    unidade = models.ForeignKey(
        Unidade, on_delete=models.PROTECT, related_name="contratos"
    )
    inquilino = models.ForeignKey(
        Inquilino, on_delete=models.PROTECT, related_name="contratos"
    )
    data_inicio = models.DateField()
    data_termino = models.DateField()
    dia_vencimento = models.PositiveSmallIntegerField()
    valor_aluguel = models.DecimalField(max_digits=10, decimal_places=2)
    valor_caucao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    numero_parcelas_caucao = models.PositiveSmallIntegerField(default=1)
    status = models.IntegerField(choices=Status.choices, default=Status.ATIVO)

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"

    def __str__(self):
        return f"Contrato #{self.id} - {self.unidade} - {self.inquilino}"


class Pagamento(models.Model):
    contrato = models.ForeignKey(
        Contrato, on_delete=models.PROTECT, related_name="pagamentos"
    )
    mes_referencia = models.CharField(max_length=7)  # formato AAAA-MM
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    valor_previsto = models.DecimalField(max_digits=10, decimal_places=2)
    valor_pago = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    comprovante = models.FileField(
        upload_to="pagamentos/comprovantes/", null=True, blank=True
    )

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        constraints = (
            models.UniqueConstraint(
                fields=["contrato", "mes_referencia"],
                name="unique_pagamento_por_mes",
            ),
        )

    def __str__(self):
        return f"Pagamento {self.mes_referencia} - {self.contrato.unidade}"

    @property
    def status_atual(self):
        if self.data_pagamento:
            return "Pago"
        if timezone.localdate() > self.data_vencimento:
            return "Atrasado"
        return "Pendente"


class Despesa(models.Model):
    class Categoria(models.IntegerChoices):
        IPTU = 1, "IPTU"
        TAXA_LIXO = 2, "Taxa de lixo"
        CONDOMINIO = 3, "Condomínio"
        AGUA = 4, "Água"
        ENERGIA = 5, "Energia"
        SEGURO = 6, "Seguro"
        MANUTENCAO = 7, "Manutenção"
        OUTRA = 8, "Outra"

    imovel = models.ForeignKey(
        Imovel, on_delete=models.PROTECT, related_name="despesas"
    )
    unidade = models.ForeignKey(
        Unidade,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="despesas",
    )
    descricao = models.CharField(max_length=150)
    categoria = models.IntegerField(choices=Categoria.choices)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    boleto = models.FileField(upload_to="despesas/boletos/", null=True, blank=True)
    comprovante = models.FileField(
        upload_to="despesas/comprovantes/", null=True, blank=True
    )

    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"

    def __str__(self):
        destino = self.unidade.identificacao if self.unidade else self.imovel.nome_imovel
        return f"{self.descricao} ({destino}) - R$ {self.valor}"

    @property
    def status_atual(self):
        if self.data_pagamento:
            return "Paga"
        if timezone.localdate() > self.data_vencimento:
            return "Atrasada"
        return "Em aberto"
