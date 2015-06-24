from libcloud.common.base import JsonResponse
from libcloud.common.base import ConnectionUserAndKey

#Endpoint for liquidweb api.
API_HOST = 'https://api.stormondemand.com'


class LiquidWebException(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message
        self.args = (code, message)

    def __str__(self):
        return "%(u) %s" % (self.code, self.message)

    def __repr__(self):
        return "LiquidWebException %u '%s'" % (self.code, self.message)


class LiquidWebResponse(JsonResponse):

    def parse_body(self):
        js = super(LiquidWebResponse).parse_body()
        return js


class LiquidWebConnection(ConnectionUserAndKey):
    host = API_HOST
    responseCls = LiquidWebResponse

    def add_default_headers(self, headers):
        pass


