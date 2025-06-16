from . import ApiView
from django.views.decorators.csrf import csrf_exempt
from django.db.models import QuerySet
from rest_framework import serializers
from ..parsers import MultiPartParser
from ..exceptions import ValidationError
from ..response import DictResponse
from .crud import CrudAPIView
from ..pagination import PageLimitPagination


class ListView(CrudAPIView):
    http_method_names = ["get"]
    pagination_class = [PageLimitPagination]


class DetailsView(CrudAPIView):
    http_method_names = ["details"]
    not_found_error_message = "Data not found."


class CreateView(CrudAPIView):
    http_method_names = ["post", "options"]
    create_success_message = "Successfully data added."
    validation_error_message = "Invalid input."


class UpdateView(CrudAPIView):
    http_method_names = ["put"]
    update_success_message = "Successfully data updated."
    not_found_error_message = "Data not found."
    validation_error_message = "Invalid input."


class DeleteView(CrudAPIView):
    http_method_names = ["delete"]
    delete_success_message = "Successfully data deleted."
    not_found_error_message = "Data not found."
