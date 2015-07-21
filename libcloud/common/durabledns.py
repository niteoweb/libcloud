import ipdb
from bs4 import BeautifulSoup

from libcloud.utils.py3 import PY3, b


from libcloud.utils.misc import lowercase_keys
from libcloud.common.base import ConnectionUserAndKey
from libcloud.common.base import XmlResponse


#API HOST to connect
API_HOST = 'durabledns.com'

SPECIAL_ERRORS = [
        'Zone does not exist'
        ]


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
        self.objects, self.errors  = self.parse_body()

    def parse_body(self):
        objects = []
        errors = []
        error_dict = {}
        zone_dict = {'type':None, 'ttl':None }
        record_dict = {}
        """
        Used to parse body from httplib.HttpResponse object.
        """
        xml_obj = super(DurableResponse, self).parse_body()
        #ipdb.set_trace()
        #parse the xml_obj
        #handle errors
        for error_el in xml_obj.iterfind('.//faultstring'):
            error_dict['ERRORMESSAGE'] = error_el.text.strip()
            error_dict['ERRORCODE'] = self.status
            errors.append(error_dict)

        #parsing response from listZonesResponse
        for response_element in xml_obj.iterfind('.//listZonesResponse'):
            for zone in response_element.iterfind('.//origin'):
                zone_dict['domain'] = zone.text.strip()
                zone_dict['id'] = zone.text.strip()
                objects.append(zone_dict)
                #reset the zone_dict for later usage
                zone_dict = {'type':None, 'ttl':None}
        #ipdb.set_trace()
        #parse response from getZoneResponse
        for getZoneResponse_el in xml_obj.iterfind('.//getZoneResponse'):
            for child in getZoneResponse_el.getchildren():
                if child.tag == 'ttl':
                    zone_dict['ttl'] = child.text.strip()
                elif child.tag == 'origin':
                    zone_dict['id'] = child.text.strip()
                    zone_dict['domain'] = child.text.strip()
            objects.append(zone_dict)
            #reset the zone_dict for later usage
            zone_dict = {'type':None, 'ttl':None}
        #parse response from listRecordsResponse
        for item in xml_obj.iterfind('.//listRecordsResponse'):
            for item in xml_obj.iterfind('.//item'):
                for child in item.getchildren():
                    if child.tag == 'id':
                        record_dict['id'] = child.text.strip()
                    elif child.tag == 'name':
                        record_dict['name'] = child.text.strip()
                    elif child.tag == 'type':
                        record_dict['type'] = child.text.strip()
                    elif child.tag == 'data':
                        record_dict['data'] = child.text.strip()
                objects.append(record_dict)
            #reset the record_dict for later usage
            record_dict = {}
        #catch Record does not exists error
        for deleteRecordResponse_el in xml_obj.iterfind('.//deleteRecordResponse'):
            for return_el in deleteRecordResponse_el.iterfind('.//return'):
                if 'Record does not exists' in return_el.text.strip():
                    errors.append({'ERRORMESSAGE':return_el.text.strip(),
                        'ERRROCODE':self.status})
        #parse response in createRecordResponse
        for createRecordResponse_el in xml_obj.iterfind('.//createRecordResponse'):
            for return_el in createRecordResponse_el.iterfind('.//return'):
                record_dict['id'] = return_el.text.strip()
                objects.append(record_dict)
                record_dict = {}

        return (objects, errors)

    def success(self):
        """
        Used to determine if the request was successful.
        """
        return len(self.errors) == 0

    def _make_excp(self, error):
        return DurableException(error['ERRORCODE', error['ERRORMESSAGE']])


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
