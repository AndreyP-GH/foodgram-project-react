from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Переопределение названия результирующего поля выдачи."""

    page_size_query_param = 'limit'
