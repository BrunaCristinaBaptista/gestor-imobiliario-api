from django.contrib import admin

from .models import Contrato, Despesa, Endereco, Imovel, Inquilino, Pagamento, Unidade


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ("id", "rua", "numero", "bairro", "cidade", "estado", "cep")
    search_fields = ("rua", "bairro", "cidade", "cep")
    list_filter = ("estado", "cidade")


class UnidadeInline(admin.TabularInline):
    model = Unidade
    extra = 1


@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ("id", "nome_imovel", "tipo_imovel", "endereco")
    search_fields = ("nome_imovel", "tipo_imovel", "endereco__rua", "endereco__cidade")
    inlines = [UnidadeInline]


@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ("id", "identificacao", "imovel", "em_manutencao", "status_atual")
    search_fields = ("identificacao", "imovel__nome_imovel")
    list_filter = ("imovel", "em_manutencao")


@admin.register(Inquilino)
class InquilinoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "sobrenome", "cpf", "telefone", "email")
    search_fields = ("nome", "sobrenome", "cpf", "email")


class PagamentoInline(admin.TabularInline):
    model = Pagamento
    extra = 0


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "unidade",
        "inquilino",
        "data_inicio",
        "data_termino",
        "valor_aluguel",
        "status",
    )
    search_fields = ("inquilino__nome", "inquilino__sobrenome", "unidade__identificacao")
    list_filter = ("status", "unidade__imovel")
    inlines = [PagamentoInline]


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "contrato",
        "mes_referencia",
        "data_vencimento",
        "valor_previsto",
        "data_pagamento",
        "status_atual",
    )
    search_fields = ("mes_referencia", "contrato__inquilino__nome")
    list_filter = ("contrato",)


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "descricao",
        "categoria",
        "imovel",
        "unidade",
        "valor",
        "data_vencimento",
        "status_atual",
    )
    search_fields = ("descricao", "imovel__nome_imovel")
    list_filter = ("categoria", "imovel")
