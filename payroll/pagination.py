from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsPagination(PageNumberPagination):
    """
    Standard pagination class for all list endpoints.

    Default page size: 20
    Max page size: 100

    Query parameters:
    - page: Page number (e.g., ?page=2)
    - page_size: Number of results per page (e.g., ?page_size=50)
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Custom paginated response format to match existing API structure.
        """
        return Response({
            'success': True,
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': data
        })
