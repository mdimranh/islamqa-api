import json

from ..parsers import MultiPartParser


class Request:
    def __init__(self, request):
        self.request = request
        self._data = None
        self._files = None
        self._full_data = None

    @property
    def data(self):
        if self.request.content_type == "application/json":
            request_body = self.request.body.decode("utf-8")
            try:
                return json.loads(request_body)
            except:
                return
        elif self.request.content_type == "multipart/form-data":
            data, files = MultiPartParser().parse(self.request)
            if files:
                self._full_data = data.copy()
                self._full_data.update(files)
            else:
                self._full_data = data
            return self._full_data
