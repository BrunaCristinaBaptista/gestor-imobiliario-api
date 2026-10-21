from math import ceil

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PaginacaoPadrao(PageNumberPagination):
    """
    Paginação da Aula 25: mantém o contrato usado nas Partes 1 a 6 (Express/FastAPI),
    { page, page_size, total_pages, results }, em vez do formato padrão do DRF
    (count, next, previous, results). Uma página além da última devolve 200 com
    results vazio, em vez de 404.
    """

    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        page_size_param = request.query_params.get(self.page_size_query_param)
        if page_size_param is not None:
            try:
                if int(page_size_param) > self.max_page_size:
                    raise ValidationError(
                        {"page_size": "O campo page_size não pode passar de 100."}
                    )
            except ValueError:
                pass

        page_size = self.get_page_size(request)
        if page_size is None:
            return None

        self.paginator = self.django_paginator_class(queryset, page_size)
        try:
            self.page_number = int(request.query_params.get(self.page_query_param, 1))
        except (TypeError, ValueError):
            raise ValidationError({"page": "Informe um número inteiro positivo."})

        if self.page_number < 1:
            raise ValidationError({"page": "Informe um número inteiro positivo."})

        self.total_pages = ceil(self.paginator.count / page_size)
        if self.total_pages == 0 or self.page_number > self.total_pages:
            self.page = None
            return []

        self.page = self.paginator.page(self.page_number)
        return list(self.page)

    def get_paginated_response(self, data):
        return Response(
            {
                "page": self.page_number,
                "page_size": self.paginator.per_page,
                "total_pages": self.total_pages,
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        # Descreve o formato acima para a documentação OpenAPI (Swagger, Etapa 6).
        return {
            "type": "object",
            "required": ["page", "page_size", "total_pages", "results"],
            "properties": {
                "page": {"type": "integer", "example": 1},
                "page_size": {"type": "integer", "example": 10},
                "total_pages": {"type": "integer", "example": 3},
                "results": schema,
            },
        }
