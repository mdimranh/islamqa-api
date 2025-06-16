from django.core.exceptions import ValidationError as DjValidationError
from rest_framework.response import Response


class RestException(Exception):
    status_code = 400
    default_message = "Bad request"

    def __init__(self, message: str = None, data: dict = None):
        self.message = message or self.default_message
        self.data = data

    def get(self, offset):
        return getattr(self, offset, None)


class ValidationError(RestException):
    status_code = 422
    default_message = "Invalid input."
    default_field_errors = {}

    def __init__(self, message: str = None, field_errors: dict = None):
        super().__init__(message=message)
        self.field = field_errors or self.default_field_errors


class InvalidToken(RestException):
    status_code = 401
    default_message = "Token is invalid."


class NotFound(RestException):
    status_code = 404
    default_message = "Data not found."


class RequiredField(RestException):
    status_code = 422
    default_message = "This field is required."
