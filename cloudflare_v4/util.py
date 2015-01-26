from . import CloudFlareError, CloudFlareAPIError

import json
import requests

def call(auth, method, endpoint, params=None):
    response = requests.request(method,
            'https://api.cloudflare.com/client/v4/' + endpoint,
            headers={ "X-Auth-Email": auth['EMAIL'],
                      "X-Auth-Key": auth['TOKEN'] },
            params=params
            )
    data = response.text
    try:
        data = json.loads(data)
        return data
    except ValueError:
        raise CloudFlareAPIError('JSON parse failed.')
    if data['result'] == 'error':
        raise CloudFlareAPIError(data['msg'])
