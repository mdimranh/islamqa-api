from django.core.paginator import Paginator

from .exceptions import NotFound


class PageLimitPagination:
    default_limit = 10
    default_page = 1
    page_query_param = "page"
    limit_query_param = "limit"

    def __init__(self, request, queryset, serializer_class):
        self.request = request
        self.queryset = queryset
        self.serializer_class = serializer_class
        self.page = self.request.GET.get(self.page_query_param, self.default_page)
        self.limit = self.request.GET.get(self.limit_query_param, self.default_limit)

    def page_obj(self):
        try:
            page_number = int(self.page)
        except ValueError:
            raise NotFound("Page number you provided is invalid.")
        paginator = Paginator(self.queryset.order_by("pk"), self.limit)
        if page_number < 1 or page_number > paginator.num_pages:
            raise NotFound("Page number you provided is invalid.")
        return paginator.get_page(page_number), paginator.count, paginator.num_pages

    def query_param_text(self, page_number):
        query_params = self.request.GET.dict()
        query_params[self.limit_query_param] = self.limit
        query_params[self.page_query_param] = page_number
        params_text = "?"
        params_text += "&".join([f"{k}={v}" for k, v in query_params.items()])
        return params_text

    def get_links(self, page_obj):
        base_path = self.request.build_absolute_uri(self.request.path)
        return {
            "next": (
                base_path + self.query_param_text(page_obj.next_page_number())
                if page_obj.has_next()
                else None
            ),
            "previous": (
                base_path + self.query_param_text(page_obj.previous_page_number())
                if page_obj.has_previous()
                else None
            ),
        }

    def data(self):
        if not self.request.GET.get(self.page_query_param) and not self.request.GET.get(
            self.limit_query_param
        ):
            return self.serializer_class(self.queryset, many=True).data
        page_obj, total_data, total_page = self.page_obj()
        return {
            "page": {
                "total": total_page,
                "current": page_obj.number,
                **self.get_links(page_obj),
            },
            "total": total_data,
            "start_index": page_obj.start_index(),
            "end_index": page_obj.end_index(),
            "data": self.serializer_class(
                instance=page_obj.object_list, many=True
            ).data,
        }
