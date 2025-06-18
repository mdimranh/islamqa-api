import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse


class DictResponse(HttpResponse):
    """
    An HTTP response class that consumes data to be serialized to JSON.

    :param data: Data to be dumped into json. By default only ``dict`` objects
      are allowed to be passed due to a security flaw before ECMAScript 5. See
      the ``safe`` parameter for more information.
    :param encoder: Should be a json encoder class. Defaults to
      ``django.core.serializers.json.DjangoJSONEncoder``.
    :param safe: Controls if only ``dict`` objects may be serialized. Defaults
      to ``True``.
    :param json_dumps_params: A dictionary of kwargs passed to json.dumps().
    """

    def __init__(
        self,
        message="",
        data=None,
        validation_error=None,
        encoder=DjangoJSONEncoder,
        safe=False,
        json_dumps_params=None,
        **kwargs,
    ):
        self.message = message
        self.data = data
        self.validation_error = validation_error
        self.encoder = encoder
        self.safe = safe
        self.json_dumps_params = json_dumps_params
        self.kwargs = kwargs
        self.data_dict = {}
        self.cookies_list = []
        if safe and not isinstance(self.data, dict):
            raise TypeError(
                "In order to allow non-dict objects to be serialized set the "
                "safe parameter to False."
            )
        if self.json_dumps_params is None:
            self.json_dumps_params = {}
        self.kwargs.setdefault("content_type", "application/json")

        if not isinstance(message, str):
            raise ValueError(f"Message should be str not {type(message)}.")

        self._data()
        data = json.dumps(self.data_dict, cls=self.encoder, **self.json_dumps_params)
        super().__init__(content=data, **self.kwargs)

    def _data(self):
        self.data_dict = {
            "message": self.message,
            "body": {"data": self.data, "field": self.validation_error},
        }

    def set_value(self, key, value):
        self.data_dict[key] = value
        data = json.dumps(self.data_dict, cls=self.encoder, **self.json_dumps_params)
        super().__init__(content=data, **self.kwargs)
        self._apply_cookies()

    def set_cookie(self, key, value=None, **kwargs):
        self.cookies_list.append((key, value, kwargs))

    def _apply_cookies(self):
        for key, value, kwargs in self.cookies_list:
            super().set_cookie(key, value, **kwargs)
