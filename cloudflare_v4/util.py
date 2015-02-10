from . import CloudFlareError, CloudFlareAPIError
from . import logger

import json
import requests

logger = logger.Logger(logger.DEBUG).getLogger()

def call(auth, method, endpoint, params=None):
    logger.debug(auth)
    logger.debug(method)
    logger.debug(endpoint)
    logger.debug(params)
    if (auth is None) or (method is None) or (endpoint is None):
        raise CloudFlareError('You must specify auth, method, and endpoint')
    else:
        response = requests.request(method,
                'https://api.cloudflare.com/client/v4/' + endpoint,
                headers={ "X-Auth-Email": auth['EMAIL'],
                          "X-Auth-Key": auth['TOKEN'] },
                params=params
                )
        data = response.text
        logger.debug(data)
        try:
            data = json.loads(data)
            return data
        except ValueError:
            raise CloudFlareAPIError('JSON parse failed.')
        if data['result'] == 'error':
            raise CloudFlareAPIError(data['msg'])
