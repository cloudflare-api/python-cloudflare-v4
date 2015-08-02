# all the exceptions
from exceptions import CloudFlareError, CloudFlareAPIError
from . import util
from . import CloudFlareError, CloudFlareAPIError
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

        def call(self, method, endpoint, params=None):
            headers = { "X-Auth-Email": self.EMAIL, "X-Auth-Key": self.TOKEN }
            url = BASE_URL + '/' +  endpoint
            method = method.upper()
            self.logger.debug("EMAIL is: " + str(self.EMAIL))
            self.logger.debug("TOKEN is: " + str(self.TOKEN))
            self.logger.debug("method type is: " + method)
            self.logger.debug("url endpoint is: " + url)
            self.logger.debug("optional params is: " + str(params))
            if (method is None) or (endpoint is None):
                raise CloudFlareError('You must specify a method and endpoint')
            else:
                if method == 'GET':
                    self.logger.debug("headers being sent: " + str(headers))
                    response = requests.get(url, headers=headers, params=params)
                elif method == 'POST':
                    headers['Content-Type'] = 'application/json'
                    self.logger.debug("headers being sent: " + str(headers))
                    response = requests.post(url, headers=headers, json=params)
                elif method == 'DELETE':
                    self.logger.debug("headers being sent: " + str(headers))
                    response = requests.delete(url, headers=headers, json=params)
                data = response.text
                self.logger.debug("data received: " + data)
                try:
                    data = json.loads(data)
                    return data
                except ValueError:
                    raise CloudFlareAPIError('JSON parse failed.')
                if data['result'] == 'error':
                    raise CloudFlareAPIError(data['msg'])

    class DynamicClient:
        def __init__(self, base_client, url_type):
            self.base_client = base_client
            self.url_type = url_type

        def get(self, params=None):
            return self.base_client.call('GET', self.url_type, params)

        def post(self, params=None):
            return self.base_client.call('POST', self.url_type, params)

        def delete(self, params=None):
            return self.base_client.call('DELETE', self.url_type, params)

    def __init__(self, email, token, debug):
        self.base_client = self.BaseClient(email, token, debug)
        setattr(self, "zones", self.DynamicClient(self.base_client, "zones"))
        setattr(self, "user", self.DynamicClient(self.base_client, "user"))
