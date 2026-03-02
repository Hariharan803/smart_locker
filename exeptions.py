from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from django.utils.timezone import now
import logging


logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        logger.error(
            f"Error occurred: {exc}",
            extra={
                "view": context.get("view").__class__.__name__,
                "status_code": response.status_code,
            }
        )

        return Response({
            "status": "error",
            "message": response.data,
            "code": response.status_code,
            "timestamp": now()
        }, status=response.status_code)

    return Response({
        "status": "error",
        "message": "Internal Server Error",
        "code": 500,
        "timestamp": now()
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)