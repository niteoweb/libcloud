from libcloud.common.base import ConnectionKey, JsonResponse


# Endpoint for nsone api
API_HOST = 'api.nsone.net'


class NsOneResponse(JsonResponse):
    pass


class NsOneConnection(ConnectionKey):
    host = API_HOST
    responseCls = NsOneResponse

    def add_default_headers(self, headers):
        headers['Content-Type'] = 'application/json'
        headers['X-NSONE-KEY'] = self.key

        return headers
