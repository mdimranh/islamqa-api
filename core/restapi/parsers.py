from django.http.multipartparser import MultiPartParser as DJMultiPartParser


class MultiPartParser:
    def parse(self, request):
        parser = DJMultiPartParser(request.META, request, request.upload_handlers)
        data, files = parser.parse()
        return data, files
