from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import (
    ContratoViewSet,
    DespesaViewSet,
    EnderecoViewSet,
    ImovelViewSet,
    InquilinoViewSet,
    PagamentoViewSet,
    UnidadeViewSet,
)

router = DefaultRouter()
router.register("enderecos", EnderecoViewSet, basename="endereco")
router.register("imoveis", ImovelViewSet, basename="imovel")
router.register("unidades", UnidadeViewSet, basename="unidade")
router.register("inquilinos", InquilinoViewSet, basename="inquilino")
router.register("contratos", ContratoViewSet, basename="contrato")
router.register("pagamentos", PagamentoViewSet, basename="pagamento")
router.register("despesas", DespesaViewSet, basename="despesa")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]

# Em desenvolvimento, o próprio Django serve os arquivos enviados (boletos e comprovantes).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
