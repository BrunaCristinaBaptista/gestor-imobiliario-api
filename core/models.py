import datetime

from django.core.exceptions import ValidationError
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

    def validar_regras(self):
        """
        Regras de negócio do contrato, num lugar só. Usada pela API (validate do
        ContratoSerializer) e pelo Django Admin (clean, abaixo).
        Levanta ValidationError com o erro no campo correspondente.
        """
        if self.data_termino <= self.data_inicio:
            raise ValidationError(
                {"data_termino": "A data de término deve ser posterior à data de início."}
            )

        if self.status != Contrato.Status.ATIVO:
            return

        # Regra 1: unidade em manutenção não recebe contrato novo.
        # Um contrato que já estava nela pode continuar sendo editado.
        unidade_anterior = (
            Contrato.objects.filter(pk=self.pk).values_list("unidade_id", flat=True).first()
        )
        if self.unidade.em_manutencao and unidade_anterior != self.unidade_id:
            raise ValidationError(
                {"unidade": "Esta unidade está em manutenção e não pode receber um novo contrato."}
            )

        # Regra 2: uma unidade não pode ter dois contratos ativos
        # com períodos que se sobrepõem.
        conflito = (
            Contrato.objects.filter(
                unidade_id=self.unidade_id,
                status=Contrato.Status.ATIVO,
                data_inicio__lte=self.data_termino,
                data_termino__gte=self.data_inicio,
            )
            .exclude(pk=self.pk)
            .first()
        )
        if conflito:
            raise ValidationError(
                {
                    "unidade": (
                        f"Esta unidade já tem o contrato #{conflito.id} ativo de "
                        f"{conflito.data_inicio:%d/%m/%Y} a {conflito.data_termino:%d/%m/%Y}, "
                        "que se sobrepõe ao período informado."
                    )
                }
            )

    def clean(self):
        # Chamado pelos formulários do Django Admin (a API não passa por aqui).
        super().clean()
        if self.dia_vencimento is not None and not 1 <= self.dia_vencimento <= 28:
            raise ValidationError({"dia_vencimento": "O dia de vencimento deve ser de 1 a 28."})
        # Só valida as regras quando os campos obrigatórios foram preenchidos;
        # se faltar algum, o próprio formulário já mostra o erro do campo.
        if self.unidade_id and self.data_inicio and self.data_termino and self.status:
            self.validar_regras()

    def gerar_cobrancas(self):
        """
        Cria um pagamento para cada mês da vigência, com vencimento no dia_vencimento
        e o valor do aluguel. Meses que já têm pagamento são mantidos como estão.
        Devolve a quantidade de cobranças criadas.
        """
        criadas = 0
        ano, mes = self.data_inicio.year, self.data_inicio.month
        while (ano, mes) <= (self.data_termino.year, self.data_termino.month):
            _, criada = self.pagamentos.get_or_create(
                mes_referencia=f"{ano}-{mes:02d}",
                defaults={
                    "data_vencimento": datetime.date(ano, mes, self.dia_vencimento),
                    "valor_previsto": self.valor_aluguel,
                },
            )
            if criada:
                criadas += 1
            mes += 1
            if mes == 13:
                ano, mes = ano + 1, 1
        return criadas


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
