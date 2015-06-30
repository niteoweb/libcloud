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
        #ipdb.set_trace()
        if PY3:
            self.body = b(self.body).decode('utf-8')
        #ipdb.set_trace()
    def parse_body(self):
        actions = None
        result_counts = None
        action_childrens = None
        data = []
        errors = []
        xml_body = super(ZonomiResponse, self).parse_body()
        #ipdb.set_trace()
        #Error handling
        if xml_body.text is not None and 'ERROR' in xml_body.text:
            errors.append(xml_body.text)

        #Data handling
        childrens = xml_body.getchildren()
        #ipdb.set_trace()
        if len(childrens) == 3:
            result_counts = childrens[1]
            actions = childrens[2]

        if actions is not None:
            actions_childrens = actions.getchildren()
            action  = actions_childrens[0]
            action_childrens = action.getchildren()

        if action_childrens is not None:
            for child in action_childrens:
                if child.tag == 'zone' or child.tag == 'record':
                    data.append(child.attrib)

        if result_counts is not None and result_counts.attrib.get('deleted') == '1':
            data.append('DELETED')

        if result_counts is not None and result_counts.attrib.get('deleted') == '0':
            errors.append(result_counts.attrib)


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
