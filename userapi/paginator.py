from rest_framework.pagination import PageNumberPagination,BasePagination
from rest_framework.response import Response


class CustomerPagination(PageNumberPagination):
    def __init__(self, per_page=5):
        self.page_size = per_page

    def get_paginated_response(self, data):
        
        return Response({
        "result": True,
        "data": data,
        "paginations": {
            "page": self.page.number,
            "per_page": self.page_size,
            "total_docs": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages
        }
    })