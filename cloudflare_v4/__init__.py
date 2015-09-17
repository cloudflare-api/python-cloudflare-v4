# all the exceptions
from .exceptions import CloudFlareError, CloudFlareAPIError
from . import logger

import json
import requests


BASE_URL = 'https://api.cloudflare.com/client/v4'

class CloudFlare(object):
    class BaseClient:
        def __init__(self, email, token, debug):
            self.EMAIL = email
            self.TOKEN = token
            self.logger = logger.Logger(debug).getLogger()

        def call(self, method, main_endpoint, endpoint=None, params=None, data=None):
            headers = { "X-Auth-Email": self.EMAIL, "X-Auth-Key": self.TOKEN }
            if endpoint is not None or (data is not None and method == 'GET'):
                url = BASE_URL + '/' +  main_endpoint + '/' + params + '/' + endpoint
            else:
                url = BASE_URL + '/' +  main_endpoint
            method = method.upper()
            self.logger.debug("EMAIL is: %s" % str(self.EMAIL))
            self.logger.debug("TOKEN is: %s" % str(self.TOKEN))
            self.logger.debug("method type is: %s" % method)
            self.logger.debug("main endpoint is: %s" % main_endpoint)
            self.logger.debug("optional endpoint is: %s" % endpoint)
            self.logger.debug("url endpoint is: %s" % url)
            self.logger.debug("optional params is: %s" % str(params))
            self.logger.debug("optional data is: %s" % str(data))
            if (method is None) or (main_endpoint is None):
                raise CloudFlareError('You must specify a method and endpoint') # should never happen
            else:
                self.logger.debug("headers being sent: %s" % str(headers))
                if method == 'GET':
                    if data:
                        params_to_send = data
                    else:
                        params_to_send = params
                    self.logger.debug("params being sent: %s", params_to_send)
                    response = requests.get(url, headers=headers,
                        params=params_to_send)
                elif method == 'POST':
                    headers['Content-Type'] = 'application/json'
                    response = requests.post(url, headers=headers, json=data)
                elif method == 'DELETE':
                    response = requests.delete("%s/%s" % (url, data), headers=headers)
                data = response.text
                self.logger.debug("data received: %s" % data)
                try:
                    data = json.loads(data)
                    if data['success'] is False:
                        raise CloudFlareAPIError(data['errors'][0]['message'])
                    else:
                        return data['result']
                except ValueError:
                    raise CloudFlareAPIError('JSON parse failed.')

    class DynamicClient:
        def __init__(self, base_client, main_endpoint, endpoint=None):
            base_client.logger.debug("base client is: %s" % str(base_client))
            base_client.logger.debug("main endpoint is: %s" % str(main_endpoint))
            base_client.logger.debug("endpoint is: %s" % str(endpoint))
            self.base_client = base_client
            self.main_endpoint = main_endpoint
            self.endpoint = endpoint

        def get(self, params=None, data=None):
            return self.base_client.call('GET', self.main_endpoint,
                self.endpoint, params, data)

        def post(self, params=None, data=None):
            return self.base_client.call('POST', self.main_endpoint,
                self.endpoint, params, data)

        def delete(self, params=None, data=None):
            return self.base_client.call('DELETE', self.main_endpoint,
                self.endpoint, params, data)

    def __init__(self, email, token, debug):
        self.base_client = self.BaseClient(email, token, debug)
        setattr(self, "zones", self.DynamicClient(self.base_client, "zones"))
        setattr(self, "user", self.DynamicClient(self.base_client, "user"))
        zones = getattr(self, "zones")
        setattr(zones, "dns_records", self.DynamicClient(self.base_client,
            "zones", "dns_records"))
        setattr(zones, "purge_cache", self.DynamicClient(self.base_client,
            "zones", "purge_cache"))
