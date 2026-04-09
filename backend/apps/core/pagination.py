from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class StandardResultsPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "current_page": self.page.number,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })


def custom_exception_handler(exc, context):
    """Standardise all API error responses."""
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "success": False,
            "status_code": response.status_code,
            "errors": response.data,
        }
        # Add a human-readable message for common codes
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            error_data["message"] = "Authentication credentials were not provided or are invalid."
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            error_data["message"] = "You do not have permission to perform this action."
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            error_data["message"] = "The requested resource was not found."
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            error_data["message"] = "Invalid request data. Please check the errors field."
        else:
            error_data["message"] = "An error occurred."

        response.data = error_data

    else:
        logger.exception("Unhandled exception in API", exc_info=exc)
        response = Response(
            {
                "success": False,
                "status_code": 500,
                "message": "An unexpected error occurred. Please try again.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
