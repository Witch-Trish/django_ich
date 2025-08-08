from rest_framework.pagination import PageNumberPagination, CursorPagination


class SubTaskPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

class DefaultCursorPagination(CursorPagination):
    page_size = 5
    ordering = '-id'