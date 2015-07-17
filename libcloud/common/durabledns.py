import ipdb
from bs4 import BeautifulSoup

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
        #because the body is decompressed so it can be logged
        if original_data:
            self.body = response._original_data
        else:
            self.body = self._decompress_response(body=response.read(),
                                                  headers=self.headers)
        if PY3:
            self.body = b(self.body).decode('utf-8')
        #xml response from durabledns not properly formatted
        #using BeautifulSoup.prettify(encoding='utf-8') to fix this issue
        b_soup = BeautifulSoup(self.body, 'xml')
        self.body = b_soup.prettify(encoding='utf-8')
        self.objects, errors  = self.parse_body()
        #ipdb.set_trace()
    def parse_body(self):
        objects = []
        errors = []
        zone_dict = {'type':None, 'ttl':None }
        """
        Used to parse body from httplib.HttpResponse object.
        """
        xml_obj = super(DurableResponse, self).parse_body()
        #parse the xml_obj
        #root = xml_obj.getroottree()
        #origin = root.xpath('//origin/text()')
        for response_element in xml_obj.iterfind('.//listZonesResponse'):
            if response_element is not None:
                for zone in response_element.iterfind('.//origin'):
                    zone_dict['domain'] = zone.text.strip()
                    zone_dict['id'] = zone.text.strip()
                    objects.append(zone_dict)
                    zone_dict = {'type':None, 'ttl':None}
        #ipdb.set_trace()
        return (objects, errors)

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

        return params

    def add_default_headers(self, headers):
        headers['Content-Type'] = 'text/xml'
        #headers['Accept'] = 'application/soap+xml, application/dime, \
        #        multipart/related, text/*'
        headers['Content-Encoding'] = 'gzip; charset=ISO-8859-1'

        return headers
