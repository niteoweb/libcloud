from libcloud.common.base import XmlResponse
from libcloud.common.base import ConnectionKey

class ZonomiResponse(XmlResponse):
    pass


class ZonomiConnection(ConnectionKey):

    def add_default_params(self, params):
        """
        Adds default parameters to perform a request,
        such as api_key.
        """
        params['api_key'] = self.key

        return params
