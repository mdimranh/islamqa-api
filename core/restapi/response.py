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
        status=200,
        **kwargs,
    ):
        self.message = message
        self.data = data
        self.validation_error = validation_error
        self.encoder = encoder
        self.safe = safe
        self.json_dumps_params = json_dumps_params or {}
        self.cookies_list = []
        
        # Validate safe parameter
        if safe and data is not None and not isinstance(data, dict):
            raise TypeError(
                "In order to allow non-dict objects to be serialized set the "
                "safe parameter to False."
            )
        
        # Validate message type
        if not isinstance(message, str):
            raise ValueError(f"Message should be str not {type(message)}.")

        # Set default content type
        kwargs.setdefault("content_type", "application/json")
        
        # Build response data
        self.data_dict = self._build_data_dict(status)
        
        # Serialize to JSON
        json_content = json.dumps(self.data_dict, cls=self.encoder, **self.json_dumps_params)
        
        # Initialize parent HttpResponse
        super().__init__(content=json_content, status=status, **kwargs)
        
        # Apply any cookies that were set
        self._apply_cookies()

    def _build_data_dict(self, status):
        """Build the response data dictionary."""
        return {
            "success": 200 <= status < 300,
            "message": self.message or "Success",
            "data": self.data,
            "error": self.validation_error,
        }

    def set_value(self, key, value):
        """Set a value in the response data and update the content."""
        self.data_dict[key] = value
        self._update_content()

    def _update_content(self):
        """Update the HTTP response content with current data_dict."""
        json_content = json.dumps(self.data_dict, cls=self.encoder, **self.json_dumps_params)
        # Update the content directly
        self.content = json_content.encode(self.charset)
        # Apply cookies after content update
        self._apply_cookies()

    def set_cookie(self, key, value=None, **kwargs):
        """Queue a cookie to be set on the response."""
        self.cookies_list.append((key, value, kwargs))
        # Apply the cookie immediately
        super().set_cookie(key, value, **kwargs)

    def _apply_cookies(self):
        """Apply all queued cookies to the response."""
        for key, value, kwargs in self.cookies_list:
            super().set_cookie(key, value, **kwargs)