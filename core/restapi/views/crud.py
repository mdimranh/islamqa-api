from enum import Enum

from django.db.models import QuerySet
from django.http import Http404
from rest_framework import serializers

from ..exceptions import ValidationError
from ..pagination import PageLimitPagination
from ..response import DictResponse
from . import ApiView


class CrudAPIView(ApiView):

    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
        "trace",
        "details",
    ]

    disabled_methods = []
    allowed_methods = None
    permission_classes = []
    permission_classes_for_get = None
    permission_classes_for_post = None
    permission_classes_for_put = None
    permission_classes_for_delete = None
    permission_classes_for_details = None
    serializer_class = None
    serializer_class_for_get = None
    serializer_class_for_post = None
    serializer_class_for_put = None
    serializer_class_for_delete = None
    serializer_class_for_details = None
    queryset = None
    pagination_class = None
    lookup_field = "id"
    lookup_field_kwargs = "id"
    filter_fields = ["status"]

    validation_error_message = "Invalid input."
    not_found_error_message = "Data not found."
    create_success_message = "Successfully data added."
    update_success_message = "Successfully data updated."
    delete_success_message = "Successfully data deleted."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None
        if self.allowed_methods and isinstance(self.allowed_methods, list):
            self.http_method_names = [method.lower() for method in self.allowed_methods]
        else:
            for method in self.disabled_methods:
                if method.lower() in self.http_method_names:
                    self.http_method_names.remove(method.lower())

    def perform_authenticate(self):
        authentication_classes = getattr(
            self, f"authentication_classes_for_{self.request.method.lower()}", None
        )
        if authentication_classes is None:
            authentication_classes = self.authentication_classes
        if authentication_classes:
            for auth_class in authentication_classes:
                user, session = auth_class().authenticate(self.request)
            if user and session:
                self.request.user = user
                self.request.session = session
                return

    def resolve_method(self):
        if self.request.method.lower() == "get" and (
            self.get_query_params(self.lookup_field) is not None
            or self.get_query_params(self.lookup_field_kwargs) is not None
        ):
            self.request.method = "DETAILS"
        return self.request

    def is_valid_url(self):
        if self.request.method.lower() not in ["get", "post"] and not (
            self.get_query_params(self.lookup_field_kwargs)
            or self.get_query_params(self.lookup_field)
        ):
            raise Http404("URL's not found.")

    def dispatch(self, request, *args, **kwargs):
        self.is_valid_url()
        self.resolve_method()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset):
        return queryset

    # def get_query(self):
    #     queryset = getattr(
    #         self, f"queryset_for_{self.request.method.lower()}", self.queryset
    #     )
    #     return queryset

    def get_query(self):
        queryset = getattr(
            self, f"queryset_for_{self.request.method.lower()}", self.queryset
        )
        if queryset is None:
            raise ValueError(
                f"No queryset provided for {self.request.method.lower()} method."
            )
        return queryset

    def get_queryset(self):
        queryset = self.get_query()
        if not isinstance(queryset, QuerySet):
            raise ValueError("Invalid queryset.")
        if self.request.method.lower() != "get":
            queryset = queryset.filter(
                **{
                    self.lookup_field: self.get_query_params(self.lookup_field)
                    or self.get_query_params(self.lookup_field_kwargs)
                }
            )
            return self.get_object(queryset).first()
        filter = {}
        for field in self.filter_fields:
            if self.request.GET.get(field):
                filter[field] = self.request.GET.get(field)
        if filter:
            queryset = queryset.filter(**filter)
        return queryset.all()

    def get_serializer_context(self):
        return {"request": self.request, "view": self}

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        serializer = (
            getattr(self, "serializer_class_for_" + self.request.method.lower(), None)
            or self.serializer_class
        )
        if serializer is None:
            raise ValueError("Serializer class not added.")
        serializer.request = self.request

        return serializer

    def get_data(self):
        queryset = self.get_queryset()
        return queryset

    def serialize_data(self):
        serializer = self.get_serializer_class()
        data = self.get_data()
        if self.request.method.lower() == "details" and data is None:
            return None
        many = self.request.method.lower() == "get"
        if many and self.pagination_class:
            paginate = self.pagination_class(self.request, data, serializer)
            return paginate.data()
        serialize = serializer(instance=data, many=many)
        return serialize.data

    def get(self, request, *args, **kwargs):
        data = self.serialize_data()
        return DictResponse(data=data, safe=False)

    def details(self, request, *args, **kwargs):
        data = self.serialize_data()
        return DictResponse(
            message=self.not_found_error_message if data is None else "",
            data=data,
            safe=False,
            status=404 if data is None else None,
        )

    def validate(self):
        serializer = self.get_serializer_class()
        data = self.request.data
        serialize = serializer(data=data)
        if not serialize.is_valid():
            raise ValidationError(
                message=self.validation_error_message, field_errors=serialize.errors
            )
        return serialize

    def performe_create(self):
        serialize = self.validate()
        serialize.save()
        return DictResponse(message=self.create_success_message, data=serialize.data)

    def post(self, request, *args, **kwargs):
        return self.performe_create()

    def perform_update(self):
        queryset = self.get_queryset()
        if queryset is None:
            return DictResponse(message="Data not found.", status=404)

        data = self.request.data
        serializer = self.get_serializer(self.get_queryset(), data=data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(
                message=self.validation_error_message, field_errors=serializer.errors
            )
        serializer.save()
        return DictResponse(message=self.update_success_message, data=serializer.data)

    def put(self, request, *args, **kwargs):
        return self.perform_update()

    def perform_delete(self):
        queryset = self.get_queryset()
        if queryset is None:
            return DictResponse(message="Data not found.", status=404)
        queryset.delete()
        return DictResponse(message=self.delete_success_message)

    def delete(self, request, *args, **kwargs):
        return self.perform_delete()
