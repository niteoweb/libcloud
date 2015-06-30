import ipdb
from libcloud.common.base import XmlResponse
from libcloud.common.base import ConnectionKey
from libcloud.utils.py3 import b, PY3


__all__ = [
        'ZonomiException',
        'ZonomiResponse',
        'ZonomiConnection'
    ]


#Endpoint for Zonomi API.
API_HOST = 'zonomi.com'

SPECIAL_ERRORS = [
        'Not found.'
    ]

class ZonomiException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        self.args = (code, message)

    def __str__(self):
        return "%s %s" % (self.code, self.message)

    def __repr__(self):
        return "ZonomiException %s %s" % (self.code, self.message)


class ZonomiResponse(XmlResponse):
    errors = None
    objects = None

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
        self.objects, self.errors = self.parse_body()
        if not self.success() and self.errors[0]['ERRORMESSAGE'] not in SPECIAL_ERRORS:
            #ipdb.set_trace()
            raise self._make_excp(self.errors[0])
        #ipdb.set_trace()
    def parse_body(self):
        error_dict = {}
        actions = None
        result_counts = None
        action_childrens = None
        data = []
        errors = []
        xml_body = super(ZonomiResponse, self).parse_body()
        #ipdb.set_trace()
        #Error handling
        if xml_body.text is not None and 'ERROR' in xml_body.text:
            error_dict['ERRORCODE'] = self.status
            error_dict['ERRORMESSAGE'] = xml_body.text
            errors.append(error_dict)

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
            error_dict['ERRORCODE'] = '404'
            error_dict['ERRORMESSAGE'] = 'Not found.'
            errors.append(error_dict)

        return (data, errors)

    def success(self):
        return (len(self.errors) == 0)

    def _make_excp(self, error):
        """
        :param error: contains error code and error message
        :type error: dict
        """
        return ZonomiException(error['ERRORCODE'], error['ERRORMESSAGE'])


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
