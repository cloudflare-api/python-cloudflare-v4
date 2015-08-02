from . import zones
from .exceptions import CloudFlareError, CloudFlareAPIError
from . import logger

import json
import requests
import logging

__all__ = [ 'CloudFlareError', 'CloudFlareAPIError',
            'zones', 'user',
            'util' ]

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
request_logger = logging.getLogger("requests.packages.urllib3")
request_logger.setLevel(logging.DEBUG)
request_logger.propagate = True

logger = logger.Logger(logger.DEBUG).getLogger()
BASE_URL = 'https://api.cloudflare.com/client/v4'

class CloudFlare(object):
    def __init__(self, email, token):
        self.EMAIL = email
        self.TOKEN = token
        self.zones = zones

    def call(self, method, endpoint, params=None):
        print self
        headers = { "X-Auth-Email": self.EMAIL, "X-Auth-Key": self.TOKEN }
        url = BASE_URL + '/' +  endpoint
        method = method.upper()
        logger.debug("auth is: " + str(auth))
        logger.debug("method type is: " + method)
        logger.debug("url endpoint is: " + url)
        logger.debug("optional params is: " + str(params))
        if (auth is None) or (method is None) or (endpoint is None):
            raise CloudFlareError('You must specify auth, method, and endpoint')
        else:
            if method == 'GET':
                logger.debug("headers being sent: " + str(headers))
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                headers['Content-Type'] = 'application/json'
                logger.debug("headers being sent: " + str(headers))
                response = requests.post(url, headers=headers, json=params)
            elif method == 'DELETE':
                logger.debug("headers being sent: " + str(headers))
                response = requests.delete(url, headers=headers, json=params)
            data = response.text
            logger.debug("data received: " + data)
            try:
                data = json.loads(data)
                return data
            except ValueError:
                raise CloudFlareAPIError('JSON parse failed.')
            if data['result'] == 'error':
                raise CloudFlareAPIError(data['msg'])
