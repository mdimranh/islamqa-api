from datetime import datetime, timedelta
from typing import Any, Dict, Type, Union

from django.db import models
from django.utils.timezone import make_aware


class DynamicFilter:
    """
    Utility class to dynamically generate filters and sorting options for Django models.
    """

    @staticmethod
    def get_filters(model_class: Type[models.Model]) -> Dict[str, Dict[str, Any]]:
        """
        Generate filter options and sorting criteria based on model fields.
        Args:
        - model_class (Type[django.db.models.Model]): The Django model class.
        Returns:
        - Dict[str, Dict[str, Any]]: A dictionary containing 'column', 'filters', 'calendar', and 'sort_by' options.
        """
        fields = model_class._meta.get_fields()

        group_by = []
        status = {}
        column = []
        filter_by = {}
        calendar = {}
        sort_by = {}

        for field in fields:
            if field.name in ["slug", "password"]:
                continue

            column.append(field.name)

            if field_type(field) == "booleanfield":
                filter_by[field.name] = [True, False]
            elif field_type(field) == "charfield":
                if hasattr(field, "choices") and field.choices:
                    if field.name.lower() == "status":
                        status = [
                            {"label": label, "value": value}
                            for value, label in field.choices
                        ]
                    else:
                        filter_by[field.name] = [
                            {"label": label, "value": value}
                            for value, label in field.choices
                        ]
                    group_by.append(field.name)
                else:
                    sort_by[field.name] = [
                        {"label": "AtoZ", "value": "asc"},
                        {"label": "ZtoA", "value": "desc"},
                    ]
                    filter_by[field.name] = {
                        "icontains": "(case-insensitive)-checks if a specified substring is present in the field.",
                        "contains": "(case-sensitive)-checks if a specified substring is present in the field.",
                        "iexact": "(case-insensitive)-checks if the field's value exactly matches the specified value.",
                        "exact": "Checks if the field's value exactly matches the specified value.",
                    }
            elif field_type(field) in ["datefield", "datetimefield"]:
                calendar[field.name] = ["exact", "range"]
                sort_by[field.name] = [
                    {"label": "Ascending", "value": "asc"},
                    {"label": "Descending", "value": "desc"},
                ]
                # Add relative date filters
                filter_by[field.name] = filter_by.get(field.name, {})
                filter_by[field.name] = [
                    {"label": "Today", "value": "today"},
                    {"label": "Yesterday", "value": "yesterday"},
                    {"label": "Tomorrow", "value": "tomorrow"},
                    {"label": "This Week", "value": "thisWeek"},
                    {"label": "Last Week", "value": "lastWeek"},
                    {"label": "Next Week", "value": "nextWeek"},
                    {"label": "This Month", "value": "thisMonth"},
                    {"label": "Last Month", "value": "lastMonth"},
                    {"label": "Next Month", "value": "nextMonth"},
                    {"label": "This Year", "value": "thisYear"},
                    {"label": "Last Year", "value": "lastYear"},
                    {"label": "Next Year", "value": "nextYear"},
                ]
            elif field_type(field) in ["integerfield", "decimalfield"]:
                sort_by[field.name] = [
                    {"label": "Ascending", "value": "asc"},
                    {"label": "Descending", "value": "desc"},
                ]
            elif field_type(field) == "foreignkeyfield":
                filter_by[field.name] = "id"

        return {
            "group_by": group_by,
            "status": status,
            "column": column,
            "filter_by": filter_by,
            "calendar": calendar,
            "sort_by": sort_by,
        }

    @staticmethod
    def apply_filters(
        model_class: Type[models.Model], method_list: Dict[str, Any]
    ) -> models.QuerySet:
        """
        Apply filters and sorting options to a queryset based on the method list provided.
        Args:
        - model_class (Type[django.db.models.Model]): The Django model class.
        - method_list (Dict[str, Any]): A dictionary containing filter and sorting options.
        Returns:
        - models.QuerySet: A queryset with the applied filters and sorting options.
        """
        queryset = model_class.objects.all()

        for method, filters in method_list.items():
            if method == "status" and filters:
                queryset = DynamicFilter.apply_status(queryset, filters)
            if method == "sort_by" and filters:
                queryset = DynamicFilter.apply_sort(queryset, filters)
            elif method == "filter_by" and filters:
                queryset = DynamicFilter.apply_other_filters(
                    queryset, model_class, filters
                )
            elif method == "calendar" and filters:
                queryset = DynamicFilter.apply_date_filters(queryset, filters)

        return queryset

    @staticmethod
    def apply_status(queryset: models.QuerySet, status: Union[str, list]):
        """
        Apply status filtering to a queryset.
        Args:
        - queryset (models.QuerySet): The queryset to filter.
        - status (Union[str, list]): The status or list of statuses to filter by.
        Returns:
        - models.QuerySet: The filtered queryset.
        """
        if isinstance(status, list):
            return queryset.filter(status__in=status)
        return queryset.filter(status=status)

    @staticmethod
    def apply_sort(
        queryset: models.QuerySet, sort_by: Dict[str, str]
    ) -> models.QuerySet:
        """
        Apply sorting options to a queryset.
        Args:
        - queryset (models.QuerySet): The queryset to sort.
        - sort_by (Dict[str, str]): A dictionary containing sorting options.
        Returns:
        - models.QuerySet: The sorted queryset.
        """
        ordering = []
        for field, direction in sort_by.items():
            if direction.lower() == "asc":
                ordering.append(field)
            elif direction.lower() == "desc":
                ordering.append(f"-{field}")
        if ordering:
            queryset = queryset.order_by(*ordering)
        return queryset

    @staticmethod
    def apply_date_filters(
        queryset: models.QuerySet, filters: Dict[str, Any]
    ) -> models.QuerySet:
        for field, value in filters.items():
            if "__range" in field:
                base_field = field.split("__")[0]
                start_date_str, end_date_str = value
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                end_date = make_aware(datetime.combine(end_date, datetime.max.time()))
                start_date = make_aware(
                    datetime.combine(start_date, datetime.min.time())
                )
                queryset = queryset.filter(
                    **{f"{base_field}__range": (start_date, end_date)}
                )
            elif "__exact" in field:
                base_field = field.split("__")[0]
                date_str = value
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                date_start = make_aware(datetime.combine(date, datetime.min.time()))
                date_end = date_start + timedelta(days=1)
                queryset = queryset.filter(
                    **{f"{base_field}__range": (date_start, date_end)}
                )
        return queryset

    @staticmethod
    def apply_other_filters(
        queryset: models.QuerySet,
        model_class: Type[models.Model],
        filters: Dict[str, Any],
    ) -> models.QuerySet:
        for field, value in filters.items():
            field_object = model_class._meta.get_field(field)
            field_object = model_class._meta.get_field(field)
            if isinstance(field_object, (models.DateField, models.DateTimeField)):
                queryset = DynamicFilter.apply_relative_date_filters(
                    queryset, field, value
                )
            elif isinstance(value, dict):
                queryset = DynamicFilter.apply_custom_filters(queryset, field, value)
            else:
                queryset = queryset.filter(**{field: value})
        return queryset

    @staticmethod
    def get_charfield_filter_type(value: str) -> str:
        """
        Determine the filter type for a CharField based on the provided value.
        Args:
        - value (str): The value to determine the filter type for.
        Returns:
        - str: The filter type ('exact', 'icontains', etc.).
        """
        if value.isnumeric():
            return "exact"
        elif value.replace(".", "", 1).isdigit():
            return "exact"
        else:
            return "icontains"

    @staticmethod
    def apply_custom_filters(
        queryset: models.QuerySet, field: str, value: Dict[str, Any]
    ) -> models.QuerySet:
        """
        Apply custom filtering to the queryset based on the provided field and value.
        Args:
        - queryset (models.QuerySet): The queryset to filter.
        - field (str): The field to filter on.
        - value (Dict[str, Any]): The filtering criteria.
        Returns:
        - models.QuerySet: The filtered queryset.
        """
        for lookup, filter_value in value.items():
            filter_expr = f"{field}__{lookup}"
            queryset = queryset.filter(**{filter_expr: filter_value})

        return queryset

    @staticmethod
    def apply_relative_date_filters(
        queryset: models.QuerySet,
        field: str,
        filter_type: str,
    ) -> models.QuerySet:
        now = make_aware(datetime.now())
        start_date = None
        end_date = None

        if filter_type == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif filter_type == "yesterday":
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        elif filter_type == "tomorrow":
            tomorrow = now + timedelta(days=1)
            start_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = tomorrow.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        elif filter_type == "thisWeek":
            start_date = now - timedelta(days=now.weekday())
            end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif filter_type == "lastWeek":
            start_date = now - timedelta(days=now.weekday() + 7)
            end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif filter_type == "nextWeek":
            start_date = now + timedelta(days=7 - now.weekday())
            end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif filter_type == "thisMonth":
            start_date = now.replace(day=1)
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(
                seconds=1
            )
        elif filter_type == "lastMonth":
            first_day_of_this_month = now.replace(day=1)
            last_month = first_day_of_this_month - timedelta(days=1)
            start_date = last_month.replace(day=1)
            end_date = (
                last_month.replace(day=last_month.day)
                + timedelta(days=1)
                - timedelta(seconds=1)
            )
        elif filter_type == "nextMonth":
            first_day_of_next_month = (now.replace(day=1) + timedelta(days=31)).replace(
                day=1
            )
            start_date = first_day_of_next_month
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(
                seconds=1
            )
        elif filter_type == "thisYear":
            start_date = now.replace(month=1, day=1)
            end_date = now.replace(
                month=12, day=31, hour=23, minute=59, second=59, microsecond=999999
            )
        elif filter_type == "lastYear":
            start_date = now.replace(year=now.year - 1, month=1, day=1)
            end_date = now.replace(
                year=now.year - 1,
                month=12,
                day=31,
                hour=23,
                minute=59,
                second=59,
                microsecond=999999,
            )
        elif filter_type == "nextYear":
            start_date = now.replace(year=now.year + 1, month=1, day=1)
            end_date = now.replace(
                year=now.year + 1,
                month=12,
                day=31,
                hour=23,
                minute=59,
                second=59,
                microsecond=999999,
            )

        # Apply the filter based on the specified field
        queryset = queryset.filter(
            models.Q(**{f"{field}__range": (start_date, end_date)})
        )

        return queryset


def field_type(field: models.Field) -> str:
    """
    Determine the type of a Django model field.
    Args:
    - field (django.db.models.Field): The Django model field.
    Returns:
    - str: Type of the field ('charfield', 'booleanfield', etc.).
    """
    if isinstance(field, models.CharField):
        return "charfield"
    elif isinstance(field, models.BooleanField):
        return "booleanfield"
    elif isinstance(field, models.IntegerField):
        return "integerfield"
    elif isinstance(field, models.DecimalField):
        return "decimalfield"
    elif isinstance(field, models.DateField):
        return "datefield"
    elif isinstance(field, models.DateTimeField):
        return "datetimefield"
    elif isinstance(field, models.OneToOneField):
        return "onetoonefield"
    elif isinstance(field, models.ForeignKey):
        return "foreignkeyfield"
    elif isinstance(field, models.ManyToManyField):
        return "manytomanyfield"
    return ""
