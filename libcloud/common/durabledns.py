from libcloud.utils.py3 import PY3, b


from libcloud.utils.misc import lowercase_keys
from libcloud.common.base import ConnectionUserAndKey
from libcloud.common.base import XmlResponse


#API HOST to connect
API_HOST = 'durabledns.com'


class DurableException(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message
        self.args = (code, message)

    def __str__(self):
        return "%s %s" % (self.code, self.message)

    def __repr__(self):
        return "DurableException %s %s" % (self.code, self.message)


class DurableResponse(XmlResponse):

    errors = []
    objects = []

    def __init__(self, response, connection):
        self.connection = connection
        self.status = response.status
        self.reason = response.reason
        self.headers = lowercase_keys(dict(response.getheaders()))

        #This attribute is set when using LoggingConnection
        original_data = getattr(response, '_original_data', None)
        #if original_data, no need to decompress the response body
        if original_data:
            self.body = response._original_data
        else:
            self.body = self._decompress_response(body=response.read(),
                                                  headers=self.headers)
        if PY3:
            self.body = b(self.body).decode('utf-8')

    def parse_body(self):
        """
        Used to parse body from httplib.HttpResponse object.
        """
        xml_body = super(DurableResponse, self).parse_body()

        return xml_body

    def success(self):
        """
        Used to determine if the request was successful.
        """
        return len(self.errors) == 0


class DurableConnection(ConnectionUserAndKey):
    host = API_HOST
    responseCls = DurableResponse

    def add_default_params(self, params):
        params['user_id'] = self.user_id
        params['key'] = self.key
