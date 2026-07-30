from rest_framework.views import exception_handler
from django.db import IntegrityError
import logging

# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger('django')


def api_exception_handler(exception, context):
    handlers={
        "ValidationError": _handle_generic_error,
        # "ValidationError": _handle_validation_error,
        "Http404": _handle_generic_error,
        "PermissionDenied": _handle_generic_error,
        "NotAuthenticated": _handle_authentication_error,
        "TypeError": _handle_generic_error
    }

    response = exception_handler(exception, context)
    print("Exception to come here....")
    logger.error("Exceptions|api_exception_handler|" + str(context['view']) + "|" + str(exception))

    if response is not None:
        # A helper example to show how response data can be modified for specific urls and status codes.
        # if AuthUserAPIView in str(context["view"]) and exception.status_code == 401:
        #     response.status_code = 200
        #     response.data = {"is_logged_in": False}
        #     return response
        response.data['status_code'] = response.status_code

    exception_class_name = exception.__class__.__name__
    if exception_class_name in handlers:
        return handlers[exception_class_name](exception, context, response)
    return response


def _handle_authentication_error(exception, context, response):
    response.data={
        "error": "Please login to proceed",
        "status_code": response.status_code
    }
    return response


# def _handle_validation_error(exception, context, response):
#     dtl_msg = ""
#
#     logger.error("Exceptions|api_exception_handler|_handle_validation_error|response:" + str(response))
#     logger.error("Exceptions|api_exception_handler|_handle_validation_error|exception:" + str(exception))
#     if isinstance(exception, dict):
#         logger.error("Exceptions|api_exception_handler|_handle_validation_error|inside dict")
#         for key in exception.keys():
#             if key != 'status_code':
#                 # dtl_msg = key + ": " + ", ".join(response.data[key])
#                 dtl_msg = ", ".join(response.data[key])
#
#     else:
#         dtl_msg = exception
#     # elif isinstance(exception, list):
#     #     logger.error("Exceptions|api_exception_handler|_handle_validation_error|inside list")
#     #     for dt in exception:
#     #         dtl_msg = dtl_msg + " " + str(dt)
#     #
#     # elif isinstance(exception, str):
#     #     logger.error("Exceptions|api_exception_handler|_handle_validation_error|inside str")
#     #     dtl_msg = str(exception)
#
#
#     logger.error("Exceptions|api_exception_handler|_handle_validation_error|dtl_msg:" + str(dtl_msg))
#     status_code = 400
#     if response is not None:
#         if response.status_code is not None:
#             status_code = response.status_code
#
#     response.data={
#         "error": dtl_msg,
#         "status_code": status_code
#     }
#     return response


def _handle_generic_error(exception, context, response):
    return response