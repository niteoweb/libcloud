import base64

import ipdb
from libcloud.common.base import JsonResponse
from libcloud.common.base import ConnectionUserAndKey
from libcloud.utils.py3 import b
from libcloud.utils.py3 import PY3

__all__ = [
        'API_HOST',
        'LiquidWebException',
        'LiquidWebResponse',
        'LiquidWebConnection',
            ]


#Endpoint for liquidweb api.
API_HOST = 'api.stormondemand.com'


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
    objects = None
    errors = None
    error_dict = {}

    def __init__(self, response, connection):
        self.connection = connection

        self.headers = dict(response.getheaders())
        self.error = response.reason
        self.status = response.status

        #This attribute is used when usng LoggingConnection
        original_data = getattr(response, '_original_data', None)

        if original_data:
            self.body = response._original_data
        else:
            self.body = self._decompress_response(body=response.read(),
                                                  headers=self.headers)

        if PY3:
            self.body = b(self.body).decode('utf-8')

        self.objects, self.errors = self.parse_body()
        if not (self.success() and self.errors[0]['ERRORMESSAGE']
                    != 'LW::Exception::RecordNotFound'):
            self._make_excp(self.errors[0])

    def parse_body(self):
        data = []
        errors = []
        js = super(LiquidWebResponse, self).parse_body()
        #ipdb.set_trace()
        if 'items' in js:
            data.append(js['items'])

        if 'name' in js:
            data.append(js)

        if 'error_class' in js:
            self.error_dict['ERRORCODE'] = self.status
            self.error_dict['ERRORMESSAGE'] = js['error_class']
            errors.append(self.error_dict)

        return (data, errors)

    def success(self):
        """
        Returns ``True`` if our request is successful.
        """
        return (len(self.errors) == 0)

    def _make_excp(self, error):
        """
        Raise LiquidWebException.
        """
        raise LiquidWebException(error['ERRORCODE'], error['ERRORMESSAGE'])


class LiquidWebConnection(ConnectionUserAndKey):
    host = API_HOST
    responseCls = LiquidWebResponse

    def add_default_headers(self, headers):
        b64string = b('%s:%s') % (self.user_id, self.key)
        encoded = base64.b64encode(b64string).decode('utf-8')
        authorization = 'Basic ' + encoded

        headers['Authorization'] = authorization
        headers['Content-Type'] = 'application/json'

        return headers

