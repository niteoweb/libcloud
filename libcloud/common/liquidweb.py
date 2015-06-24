import base64

from libcloud.common.base import JsonResponse
from libcloud.common.base import ConnectionUserAndKey
from libcloud.utils.py3 import b
from libcloud.utils.py3 import PY3

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

    def __init__(self, response, connection):
        self.connection = connection

        self.headers = dict(response.get_headers)
        self.error = response.reason
        self.status = response.status

        #This attribute is used when usng LoggingConnection
        original_data = getattr(response, '_original_data', None)

        if original_data:
            self.body = response._original_data
        else:
            self.body = self._decompress_response(body=response.read(),
                                                  headers=self.headers())

        if PY3:
            self.body = b(self.body).decode('utf-8')

    def parse_body(self):
        js = super(LiquidWebResponse).parse_body()
        return js


class LiquidWebConnection(ConnectionUserAndKey):
    host = API_HOST
    responseCls = LiquidWebResponse

    def add_default_headers(self, headers):
        b64string = b('%s:%s') % (self.user_id, self.key)
        encoded = base64.b64encode(b64string).decode('utf-8')
        authorization = 'Basic ' + encoded

        headers['Authorization'] = authorization

        return headers


