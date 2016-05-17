
from logger import Logger
from utils import sanitize_secrets
from read_configs import read_configs
from api_v4 import api_v4
from api_extras import api_extras

from exceptions import CloudFlareError, CloudFlareAPIError, CloudFlareInternalError

import json
import requests
import urllib

BASE_URL = 'https://api.cloudflare.com/client/v4'

class CloudFlare(object):
	class _base:
		def __init__(self, email, token, certtoken, base_url, debug):
			self.EMAIL = email
			self.TOKEN = token
			self.CERTTOKEN = certtoken
			self.BASE_URL = base_url

			if debug:
				self.logger = logger.Logger(debug).getLogger()
			else:
				self.logger = None

		def _call_with_no_auth(self, method, api_call_part1, api_call_part2=None, api_call_part3=None, identifier1=None, identifier2=None, params=None, data=None):
			headers = {}
			return self._call(method, headers, api_call_part1, api_call_part2, api_call_part3, identifier1, identifier2, params, data)

		def _call_with_auth(self, method, api_call_part1, api_call_part2=None, api_call_part3=None, identifier1=None, identifier2=None, params=None, data=None):
			if self.EMAIL is '' or self.TOKEN is '':
				raise CloudFlareAPIError(0, 'no email and/or token defined')
			headers = { "X-Auth-Email": self.EMAIL, "X-Auth-Key": self.TOKEN, 'Content-Type': 'application/json' }
			return self._call(method, headers, api_call_part1, api_call_part2, api_call_part3, identifier1, identifier2, params, data)

		def _call_with_certauth(self, method, api_call_part1, api_call_part2=None, api_call_part3=None, identifier1=None, identifier2=None, params=None, data=None):
			if self.CERTTOKEN is '':
				raise CloudFlareAPIError(0, 'no email and/or cert token defined')
			headers = { "X-Auth-User-Service-Key": self.CERTTOKEN, 'Content-Type': 'application/json' }
			return self._call(method, headers, api_call_part1, api_call_part2, api_call_part3, identifier1, identifier2, params, data)

		def _call(self, method, headers, api_call_part1, api_call_part2=None, api_call_part3=None, identifier1=None, identifier2=None, params=None, data=None):
			if api_call_part2 is not None or (data is not None and method == 'GET'):
				if identifier2 is None:
					url = self.BASE_URL + '/' + api_call_part1 + '/' + identifier1 + '/' + api_call_part2
				else:
					url = self.BASE_URL + '/' + api_call_part1 + '/' + identifier1 + '/' + api_call_part2 + '/' + identifier2
			else:
				if identifier1 is None:
					url = self.BASE_URL + '/' + api_call_part1
				else:
					url = self.BASE_URL + '/' + api_call_part1 + '/' + identifier1
			if api_call_part3:
				url += '/' + api_call_part3

			if self.logger:
				self.logger.debug("Call: %s,%s,%s,%s,%s" % (str(api_call_part1), str(identifier1), str(api_call_part2), str(identifier2), str(api_call_part3)))
				self.logger.debug("Call: optional params and data: %s %s" % (str(params), str(data)))
				self.logger.debug("Call: url is: %s" % (str(url)))
				self.logger.debug("Call: method is: %s" % (str(method)))
				self.logger.debug("Call: headers %s" % str(utils.sanitize_secrets(headers)))

			if (method is None) or (api_call_part1 is None):
				raise CloudFlareInternalError('You must specify a method and endpoint') # should never happen

			method = method.upper()

			if method == 'GET':
				response = requests.get(url, headers=headers, params=params, data=data)
			elif method == 'POST':
				response = requests.post(url, headers=headers, params=params, json=data)
			elif method == 'PUT':
				response = requests.put(url, headers=headers, params=params, json=data)
			elif method == 'DELETE':
				if data:
					response = requests.delete(url, headers=headers, json=data)
				else:
					response = requests.delete(url, headers=headers)
			elif method == 'PATCH':
				if data:
					response = requests.request('PATCH', url, headers=headers, params=params, json=data)
				else:
					response = requests.request('PATCH', url, headers=headers, params=params)
			else:
				raise CloudFlareAPIError(0, 'method not supported') # should never happen

			if self.logger:
				self.logger.debug("Response url: %s", response.url)

			response_data = response.text
			if self.logger:
				self.logger.debug("Response_data: %s" % response_data)
			try:
				response_data = json.loads(response_data)
			except ValueError:
				raise CloudFlareAPIError(0, 'JSON parse failed.')

			if response_data['success'] is False:
				if self.logger:
					self.logger.debug("response_data error: %d %s" % (response_data['errors'][0]['code'], response_data['errors'][0]['message']))
				raise CloudFlareAPIError(response_data['errors'][0]['code'], response_data['errors'][0]['message'])

			return response_data['result']

	class _unused:
		def __init__(self, base, api_call_part1, api_call_part2=None, api_call_part3=None):
			#if self.logger:
			#	self.logger.debug("_unused %s,%s,%s" % (str(base), str(api_call_part1), str(api_call_part2)))
			self.base = base
			self.api_call_part1 = api_call_part1
			self.api_call_part2 = api_call_part2
			self.api_call_part3 = api_call_part3

	class _client_noauth:
		def __init__(self, base, api_call_part1, api_call_part2=None, api_call_part3=None):
			#if self.logger:
			#	self.logger.debug("_client_noauth %s,%s,%s" % (str(base), str(api_call_part1), str(api_call_part2)))
			self.base = base
			self.api_call_part1 = api_call_part1
			self.api_call_part2 = api_call_part2
			self.api_call_part3 = api_call_part3

		def get(self, identifier1=None, identifier2=None, params=None, data=None):
			return self.base._call_with_no_auth('GET', self.api_call_part1, self.api_call_part2, self.api_call_part3, identifier1, identifier2, params, data)

	class _client_with_auth:
		def __init__(self, base, api_call_part1, api_call_part2=None, api_call_part3=None):
			#if self.logger:
			#	self.logger.debug("_client_with_auth %s,%s,%s" % (str(base), str(api_call_part1), str(api_call_part2)))
			self.base = base
			self.api_call_part1 = api_call_part1
			self.api_call_part2 = api_call_part2
			self.api_call_part3 = api_call_part3

		def get(self, identifier1=None, identifier2=None, params=None, data=None):
			return self.base._call_with_auth('GET', self.api_call_part1, self.api_call_part2, self.api_call_part3, identifier1, identifier2, params, data)

		def patch(self, identifier1=None, identifier2=None, params=None, data=None):
			return self.base._call_with_auth('PATCH', self.api_call_part1, self.api_call_part2, self.api_call_part3, identifier1, identifier2, params, data)

		def post(self, identifier1=None, identifier2=None, params=None, data=None):
			return self.base._call_with_auth('POST', self.api_call_part1, self.api_call_part2, self.api_call_part3, identifier1, identifier2, params, data)

		def put(self, identifier1=None, identifier2=None, params=None, data=None):
			return self.base._call_with_auth('PUT', self.api_call_part1, self.api_call_part2, self.api_call_part3, identifier1, identifier2, params, data)

		def delete(self, identifier1=None, identifier2=None, params=None, data=None):
			return self.base._call_with_auth('DELETE', self.api_call_part1, self.api_call_part2, self.api_call_part3, identifier1, identifier2, params, data)

	class _client_with_cert_auth:
		def __init__(self, base, api_call_part1, api_call_part2=None, api_call_part3=None):
			#if self.logger:
			#	self.logger.debug("_client_with_cert_auth %s,%s,%s" % (str(base), str(api_call_part1), str(api_call_part2)))
			self.base = base
			self.api_call_part1 = api_call_part1
			self.api_call_part2 = api_call_part2
			self.api_call_part3 = api_call_part3

		def get(self, identifier1=None, identifier2=None, params=None, data=None):
			return self.base._call_with_certauth('GET', self.api_call_part1, self.api_call_part2, self.api_call_part3, identifier1, identifier2, params, data)

		def patch(self, identifier1=None, identifier2=None, params=None, data=None):
			return self.base._call_with_certauth('PATCH', self.api_call_part1, self.api_call_part2, self.api_call_part3, identifier1, identifier2, params, data)

		def post(self, identifier1=None, identifier2=None, params=None, data=None):
			return self.base._call_with_certauth('POST', self.api_call_part1, self.api_call_part2, self.api_call_part3, identifier1, identifier2, params, data)

		def put(self, identifier1=None, identifier2=None, params=None, data=None):
			return self.base._call_with_certauth('PUT', self.api_call_part1, self.api_call_part2, self.api_call_part3, identifier1, identifier2, params, data)

		def delete(self, identifier1=None, identifier2=None, params=None, data=None):
			return self.base._call_with_certauth('DELETE', self.api_call_part1, self.api_call_part2, self.api_call_part3, identifier1, identifier2, params, data)

	def __init__(self, email=None, token=None, certtoken=None, debug=False):
		base_url = BASE_URL

		# class creation values override configuration values
		[ conf_email, conf_token, conf_certtoken, extras ] = read_configs()

		if email is None:
			email = conf_email
		if token is None:
			token = conf_token
		if certtoken is None:
			certtoken = conf_certtoken

		# Removed: There are cases where you don't need an email and token
		# if email is None or token is None:
		# 	raise CloudFlareInternalError('You must at least specify an email and token string')

		self.base = self._base(email, token, certtoken, base_url, debug)

		# add the API calls
		api_v4(self)
		if extras:
			api_extras(self, extras)

