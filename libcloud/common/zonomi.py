from libcloud.common.base import XmlResponse
from libcloud.common.base import ConnectionKey

__all__ = [
        'ZonomiResponse',
        'ZonomiConnection'
    ]


#Endpoint for Zonomi API.
API_HOST = 'https://zonomi.com/app/dns/dyndns.jsp?'

class ZonomiResponse(XmlResponse):
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
        return headers
