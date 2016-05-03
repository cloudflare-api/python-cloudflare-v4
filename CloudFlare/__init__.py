# all the exceptions

from logger import Logger
from utils import sanitize_secrets
from read_configs import read_configs

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

        def _call_with_no_auth(self, method, api_call_part1, api_call_part2=None, identifier1=None, identifier2=None, params=None, data=None):
	    headers = {}
	    return self._call(method, headers, api_call_part1, api_call_part2, identifier1, identifier2, params, data)

        def _call_with_auth(self, method, api_call_part1, api_call_part2=None, identifier1=None, identifier2=None, params=None, data=None):
	    if self.EMAIL is '' or self.TOKEN is '':
                raise CloudFlareAPIError(0, 'no email and/or token defined')
            headers = { "X-Auth-Email": self.EMAIL, "X-Auth-Key": self.TOKEN, 'Content-Type': 'application/json' }
	    return self._call(method, headers, api_call_part1, api_call_part2, identifier1, identifier2, params, data)

        def _call_with_certauth(self, method, api_call_part1, api_call_part2=None, identifier1=None, identifier2=None, params=None, data=None):
	    if self.EMAIL is '' or self.CERTTOKEN is '':
                raise CloudFlareAPIError(0, 'no email and/or cert token defined')
            headers = { "X-Auth-Email": self.EMAIL, "X-Auth-User-Service-Key": self.CERTTOKEN, 'Content-Type': 'application/json' }
	    return self._call(method, headers, api_call_part1, api_call_part2, identifier1, identifier2, params, data)

        def _call(self, method, headers, api_call_part1, api_call_part2=None, identifier1=None, identifier2=None, params=None, data=None):
            if api_call_part2 is not None or (data is not None and method == 'GET'):
		if identifier2 is None:
                    url = self.BASE_URL + '/' +  api_call_part1 + '/' + identifier1 + '/' + api_call_part2
		else:
                    url = self.BASE_URL + '/' +  api_call_part1 + '/' + identifier1 + '/' + api_call_part2 + '/' + identifier2
            else:
		if identifier1 is None:
		    url = self.BASE_URL + '/' +  api_call_part1
		else:
		    url = self.BASE_URL + '/' +  api_call_part1 + '/' + identifier1

	    if self.logger:
	        self.logger.debug("Call: %s,%s,%s,%s" % (str(api_call_part1), str(identifier1), str(api_call_part2), str(identifier2)))
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
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
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
        def __init__(self, base, api_call_part1, api_call_part2=None):
	    #if self.logger:
	    #    self.logger.debug("_unused %s,%s,%s" % (str(base), str(api_call_part1), str(api_call_part2)))
            self.base = base
            self.api_call_part1 = api_call_part1
            self.api_call_part2 = api_call_part2

    class _client_noauth:
        def __init__(self, base, api_call_part1, api_call_part2=None):
	    #if self.logger:
	    #    self.logger.debug("_client_noauth %s,%s,%s" % (str(base), str(api_call_part1), str(api_call_part2)))
            self.base = base
            self.api_call_part1 = api_call_part1
            self.api_call_part2 = api_call_part2

        def get(self, identifier1=None, identifier2=None, params=None, data=None):
            return self.base._call_with_no_auth('GET', self.api_call_part1, self.api_call_part2, identifier1, identifier2, params, data)

    class _client_with_auth:
        def __init__(self, base, api_call_part1, api_call_part2=None):
	    #if self.logger:
	    #    self.logger.debug("_client_with_auth %s,%s,%s" % (str(base), str(api_call_part1), str(api_call_part2)))
            self.base = base
            self.api_call_part1 = api_call_part1
            self.api_call_part2 = api_call_part2

        def get(self, identifier1=None, identifier2=None, params=None, data=None):
            return self.base._call_with_auth('GET', self.api_call_part1, self.api_call_part2, identifier1, identifier2, params, data)

        def patch(self, identifier1=None, identifier2=None, params=None, data=None):
            return self.base._call_with_auth('PATCH', self.api_call_part1, self.api_call_part2, identifier1, identifier2, params, data)

        def post(self, identifier1=None, identifier2=None, params=None, data=None):
            return self.base._call_with_auth('POST', self.api_call_part1, self.api_call_part2, identifier1, identifier2, params, data)

        def put(self, identifier1=None, identifier2=None, params=None, data=None):
            return self.base._call_with_auth('PUT', self.api_call_part1, self.api_call_part2, identifier1, identifier2, params, data)

        def delete(self, identifier1=None, identifier2=None, params=None, data=None):
            return self.base._call_with_auth('DELETE', self.api_call_part1, self.api_call_part2, identifier1, identifier2, params, data)

    class _client_with_cert_auth:
        def __init__(self, base, api_call_part1, api_call_part2=None):
	    #if self.logger:
	    #    self.logger.debug("_client_with_cert_auth %s,%s,%s" % (str(base), str(api_call_part1), str(api_call_part2)))
            self.base = base
            self.api_call_part1 = api_call_part1
            self.api_call_part2 = api_call_part2

        def get(self, identifier1=None, identifier2=None, params=None, data=None):
            return self.base._call_with_certauth('GET', self.api_call_part1, self.api_call_part2, identifier1, identifier2, params, data)

        def patch(self, identifier1=None, identifier2=None, params=None, data=None):
            return self.base._call_with_certauth('PATCH', self.api_call_part1, self.api_call_part2, identifier1, identifier2, params, data)

        def post(self, identifier1=None, identifier2=None, params=None, data=None):
            return self.base._call_with_certauth('POST', self.api_call_part1, self.api_call_part2, identifier1, identifier2, params, data)

        def put(self, identifier1=None, identifier2=None, params=None, data=None):
            return self.base._call_with_certauth('PUT', self.api_call_part1, self.api_call_part2, identifier1, identifier2, params, data)

        def delete(self, identifier1=None, identifier2=None, params=None, data=None):
            return self.base._call_with_certauth('DELETE', self.api_call_part1, self.api_call_part2, identifier1, identifier2, params, data)

    def __init__(self, email=None, token=None, certtoken=None, debug=False):
	base_url = BASE_URL

	# class creation values override configuration values
	[ conf_email, conf_token, conf_certtoken ] = read_configs()

	if email is None:
		email = conf_email
	if token is None:
		token = conf_token
	if certtoken is None:
		certtoken = conf_certtoken

	#if email is None or token is None:
	#	raise CloudFlareInternalError('You must at least specify an email and token string')

	self.base = self._base(email, token, certtoken, base_url, debug)

	# The API commands for /user/
	setattr(self, "user", self._client_with_auth(self.base, "user"))
	user = getattr(self, "user")
	setattr(user, "billing", self._unused(self.base, "user/billing"))
	user_billing = getattr(user, "billing")
	setattr(user_billing, "history", self._client_with_auth(self.base, "user/billing/history"))
	setattr(user_billing, "profile", self._client_with_auth(self.base, "user/billing/profile"))
	setattr(user_billing, "subscriptions", self._unused(self.base, "user/billing/subscriptions"))
	user_billing_subscriptions = getattr(user_billing, "subscriptions")
	setattr(user_billing_subscriptions, "apps", self._client_with_auth(self.base, "user/billing/subscriptions/apps"))
	setattr(user_billing_subscriptions, "zones", self._client_with_auth(self.base, "user/billing/subscriptions/zones"))
	setattr(user, "firewall", self._unused(self.base, "user/firewall"))
	user_firewall = getattr(user, "firewall")
	setattr(user_firewall, "access_rules", self._unused(self.base, "user/firewall/access_rules"))
	user_firewall_access_rules = getattr(user_firewall, "access_rules")
	setattr(user_firewall_access_rules, "rules", self._client_with_auth(self.base, "user/firewall/access_rules/rules"))
	setattr(user, "organizations", self._client_with_auth(self.base, "user/organizations"))
	setattr(user, "invites", self._client_with_auth(self.base, "user/invites"))
	setattr(user, "virtual_dns", self._client_with_auth(self.base, "user/virtual_dns"))

	# The API commands for /zones/
	setattr(self, "zones", self._client_with_auth(self.base, "zones"))
	zones = getattr(self, "zones")
	setattr(zones, "activation_check", self._client_with_auth(self.base, "zones", "activation_check"))
	setattr(zones, "available_plans", self._client_with_auth(self.base, "zones", "available_plans"))
	setattr(zones, "custom_certificates", self._client_with_auth(self.base, "zones", "custom_certificates"))
	zones_custom_certificates = getattr(zones, "custom_certificates")
	setattr(zones_custom_certificates, "prioritize", self._client_with_auth(self.base, "zones", "custom_certificates/prioritize"))
	setattr(zones, "custom_pages", self._client_with_auth(self.base, "zones", "custom_pages"))
	setattr(zones, "dns_records", self._client_with_auth(self.base, "zones", "dns_records"))
	setattr(zones, "keyless_certificates", self._client_with_auth(self.base, "zones", "keyless_certificates"))
	setattr(zones, "pagerules", self._client_with_auth(self.base, "zones", "pagerules"))
	setattr(zones, "purge_cache", self._client_with_auth(self.base, "zones", "purge_cache"))
	setattr(zones, "railguns", self._client_with_auth(self.base, "zones", "railguns"))
	setattr(zones, "settings", self._client_with_auth(self.base, "zones", "settings"))
	zones_settings = getattr(zones, "settings")
	setattr(zones_settings, "advanced_ddos", self._client_with_auth(self.base, "zones", "settings/advanced_ddos"))
	setattr(zones_settings, "always_online", self._client_with_auth(self.base, "zones", "settings/always_online"))
	setattr(zones_settings, "browser_cache_ttl", self._client_with_auth(self.base, "zones", "settings/browser_cache_ttl"))
	setattr(zones_settings, "browser_check", self._client_with_auth(self.base, "zones", "settings/browser_check"))
	setattr(zones_settings, "cache_level", self._client_with_auth(self.base, "zones", "settings/cache_level"))
	setattr(zones_settings, "challenge_ttl", self._client_with_auth(self.base, "zones", "settings/challenge_ttl"))
	setattr(zones_settings, "development_mode", self._client_with_auth(self.base, "zones", "settings/development_mode"))
	setattr(zones_settings, "email_obfuscation", self._client_with_auth(self.base, "zones", "settings/email_obfuscation"))
	setattr(zones_settings, "hotlink_protection", self._client_with_auth(self.base, "zones", "settings/hotlink_protection"))
	setattr(zones_settings, "ip_geolocation", self._client_with_auth(self.base, "zones", "settings/ip_geolocation"))
	setattr(zones_settings, "ipv6", self._client_with_auth(self.base, "zones", "settings/ipv6"))
	setattr(zones_settings, "minify", self._client_with_auth(self.base, "zones", "settings/minify"))
	setattr(zones_settings, "mirage", self._client_with_auth(self.base, "zones", "settings/mirage"))
	setattr(zones_settings, "mobile_redirect", self._client_with_auth(self.base, "zones", "settings/mobile_redirect"))
	setattr(zones_settings, "origin_error_page_pass_thru", self._client_with_auth(self.base, "zones", "settings/origin_error_page_pass_thru"))
	setattr(zones_settings, "polish", self._client_with_auth(self.base, "zones", "settings/polish"))
	setattr(zones_settings, "prefetch_preload", self._client_with_auth(self.base, "zones", "settings/prefetch_preload"))
	setattr(zones_settings, "response_buffering", self._client_with_auth(self.base, "zones", "settings/response_buffering"))
	setattr(zones_settings, "rocket_loader", self._client_with_auth(self.base, "zones", "settings/rocket_loader"))
	setattr(zones_settings, "security_header", self._client_with_auth(self.base, "zones", "settings/security_header"))
	setattr(zones_settings, "security_level", self._client_with_auth(self.base, "zones", "settings/security_level"))
	setattr(zones_settings, "server_side_exclude", self._client_with_auth(self.base, "zones", "settings/server_side_exclude"))
	setattr(zones_settings, "sort_query_string_for_cache", self._client_with_auth(self.base, "zones", "settings/sort_query_string_for_cache"))
	setattr(zones_settings, "ssl", self._client_with_auth(self.base, "zones", "settings/ssl"))
	setattr(zones_settings, "tls_1_2_only", self._client_with_auth(self.base, "zones", "settings/tls_1_2_only"))
	setattr(zones_settings, "tls_client_auth", self._client_with_auth(self.base, "zones", "settings/tls_client_auth"))
	setattr(zones_settings, "true_client_ip_header", self._client_with_auth(self.base, "zones", "settings/true_client_ip_header"))
	setattr(zones_settings, "waf", self._client_with_auth(self.base, "zones", "settings/waf"))
	setattr(zones, "analytics", self._unused(self.base, "zones", "analytics"))
	zones_analytics = getattr(zones, "analytics")
	setattr(zones_analytics, "colos", self._client_with_auth(self.base, "zones", "analytics/colos"))
	setattr(zones_analytics, "dashboard", self._client_with_auth(self.base, "zones", "analytics/dashboard"))
	setattr(zones, "firewall", self._unused(self.base, "zones", "firewall"))
	zones_firewall = getattr(zones, "firewall")
	setattr(zones_firewall, "access_rules", self._unused(self.base, "zones", "firewall/access_rules"))
	zones_firewall_access_rules = getattr(zones_firewall, "access_rules")
	setattr(zones_firewall_access_rules, "rules", self._client_with_auth(self.base, "zones", "firewall/access_rules/rules"))

	# The API commands for /railguns/
	setattr(self, "railguns", self._client_with_auth(self.base, "railguns"))
	railguns = getattr(self, "railguns")
	setattr(railguns, "zones", self._client_with_auth(self.base, "railguns", "zones"))

	# The API commands for /organizations/
	setattr(self, "organizations", self._client_with_auth(self.base, "organizations"))
	organizations = getattr(self, "organizations")
	setattr(organizations, "members", self._client_with_auth(self.base, "organizations", "members"))
	setattr(organizations, "invites", self._client_with_auth(self.base, "organizations", "invites"))
	setattr(organizations, "railguns", self._client_with_auth(self.base, "organizations", "railguns"))
	setattr(organizations, "roles", self._client_with_auth(self.base, "organizations", "roles"))
	setattr(organizations, "firewall", self._unused(self.base, "organizations", "firewall"))
	organizations_firewall = getattr(organizations, "firewall")
	setattr(organizations_firewall, "access_rules", self._unused(self.base, "organizations", "firewall/access_rules"))
	organizations_firewall_access_rules = getattr(organizations_firewall, "access_rules")
	setattr(organizations_firewall_access_rules, "rules", self._client_with_auth(self.base, "organizations", "firewall/access_rules/rules"))
	setattr(organizations, "virtual_dns", self._client_with_auth(self.base, "organizations", "virtual_dns"))

	# The API commands for /certificates/
	setattr(self, "certificates", self._client_with_cert_auth(self.base, "certificates"))

	# The API commands for /ips/
	setattr(self, "ips", self._client_noauth(self.base, "ips"))

	# The DNSSEC commands
	setattr(zones, "dnssec", self._client_with_auth(self.base, "zones", "dnssec"))
	zones_dnssec = getattr(zones, "dnssec")
	setattr(zones_dnssec, "status", self._client_with_auth(self.base, "zones", "dnssec/status"))

	# EXTRAS
	# /zones/:zone_id/ssl/certificate_packs
	setattr(zones, "ssl", self._client_with_auth(self.base, "zones", "ssl"))
	zones_ssl = getattr(zones, "ssl")
	setattr(zones_ssl, "certificate_packs", self._client_with_auth(self.base, "zones", "ssl/certificate_packs"))

