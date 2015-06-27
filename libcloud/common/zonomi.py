import ipdb
from libcloud.common.base import XmlResponse
from libcloud.common.base import ConnectionKey
from libcloud.utils.py3 import b, PY3


__all__ = [
        'ZonomiResponse',
        'ZonomiConnection'
    ]


#Endpoint for Zonomi API.
API_HOST = 'zonomi.com'

class ZonomiResponse(XmlResponse):

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

    def parse_body(self):
        data = []
        errors = []
        xml_body = super(ZonomiResponse, self).parse_body()
        childrens = xml_body.getchildren()
        actions = childrens[2]
        actions_childrens = actions.getchildren()
        action  = actions_childrens[0]
        action_childrens = action.getchildren()
        for child in action_childrens:
            if child.tag == 'zone':
                data.append(child.attrib)

        return (data, errors)

    def success(self):
        pass

    def _make_excp(self):
        pass


class ZonomiConnection(ConnectionKey):
    host = API_HOST
    responseCls = ZonomiResponse

    def add_default_params(self, params):
        """
        Adds default parameters to perform a request,
        such as api_key.
        """
        params['api_key'] = self.key

        return params

    def add_default_headers(self, headers):
        """
        Adds default headers needed to perform a successful
        request such as Content-Type, User-Agent.
        """
        headers['Content-Type'] = 'text/xml;charset=UTF-8'

        return headers
