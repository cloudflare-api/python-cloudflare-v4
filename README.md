# cloudflare


## Credit

This is based on work by [Felix Wong (gnowxilef)](https://github.com/gnowxilef) found [here](https://github.com/cloudflare-api/python-cloudflare-v4).  It has been seriously expanded upon.

## Copyright

Portions copyright [Felix Wong (gnowxilef)](https://github.com/gnowxilef) 2015 and CloudFlare 2016.

## CloudFlare API version 4

The CloudFlare API can be found [here](https://api.cloudflare.com/). Each API call is provided via a similarly named function within the _CloudFlare_ class. A full list is provided below.

## Installation

```bash
	./setup.py build
	sudo ./setup.py install
```

Or whatever variance of that you want to use.

## Getting Started

A very simple listing of zones within your account; including the IPv6 status of the zone.

```python
import CloudFlare

def main():
	cf = CloudFlare.CloudFlare()
	zones = cf.zones.get(params = {'per_page':50})
	for zone in zones:
		zone_name = zone['name']
		zone_id = zone['id']
		settings_ipv6 = cf.zones.settings.ipv6.get(zone_id)
		ipv6_status = settings_ipv6['value']
		settings_ssl = cf.zones.settings.ssl.get(zone_id)
		ssl_status = settings_ssl['value']
		print zone_id, ssl_status, ipv6_status, zone_name

if __name__ == '__main__':
	main()
```

A more complex example follows.

```python
import sys
import CloudFlare

def main():
	zone_name = 'example.com'

	cf = CloudFlare.CloudFlare()

	# query for the zone name and expect only one value back
	try:
		zones = cf.zones.get(params = {'name':zone_name,'per_page':1})
	except CloudFlare.CloudFlareAPIError as e:
		exit('/zones.get %d %s - api call failed' % (e, e))
	except Exception as e:
		exit('/zones.get - %s - api call failed' % (e))

	# extract the zone_id which is needed to process that zone
	zone = zones[0]
	zone_id = zone['id']

	# request the DNS records from that zone
	try:
		dns_records = cf.zones.dns_records.get(zone_id)
	except CloudFlare.CloudFlareAPIError as e:
		exit('/zones/dns_records.get %d %s - api call failed' % (e, e))

	# print the results - first the zone name
	print zone_id, zone_name

	# then all the DNS records for that zone
	for dns_record in dns_records:
		r_name = dns_record['name']
		r_type = dns_record['type']
		r_value = dns_record['content']
		r_id = dns_record['id']
		print '\t', r_id, r_name, r_type, r_value

	exit(0)

if __name__ == '__main__':
	main()
```

## Providing CloudFlare Username and API Key

When you create a _CloudFlare_ class you can pass up to three paramaters.

 * Account email
 * Account API key
 * Optional Debug flag (True/False)

If the account email and API key are not passed when you create the class, then they are retreived from either the users exported shell environment variables or the .cloudflare.cfg or ~/.cloudflare.cfg or ~/.cloudflare/cloudflare.cfg files, in that order.

There is one call that presently doesn't need any email or token certification (the */ips* call); hence you can test without any values saved away.

### Using shell environment variables
```bash
$ export CF_API_EMAIL='user@example.com'
$ export CF_API_KEY='00000000000000000000000000000000'
$ export CF_API_CERTKEY='v1.0-...'
$
```

### Using configuration file to store email and keys

```bash
$ cat ~/.cloudflare/cloudflare.cfg 
[CloudFlare]
email = user@example.com
token = 00000000000000000000000000000000
certoken = v1.0-...
$
```

The *CF_API_CERTKEY* or *certtoken* values are used for the Origin-CA */certificates* API calls.

## Included example code

The *examples* folder contains many examples in both simple and verbose formats.

## A DNS zone code example

```python
#!/usr/bin/env python

import sys
import CloudFlare

def main():
	zone_name = sys.argv[1]
	cf = CloudFlare.CloudFlare()
	zone_info = cf.zones.post(data={'jump_start':False, 'name': zone_name})
	zone_id = zone_info['id']

	dns_records = [
		{'name':'foo', 'type':'AAAA', 'content':'2001:d8b::1'},
		{'name':'foo', 'type':'A', 'content':'192.168.0.1'},
		{'name':'duh', 'type':'A', 'content':'10.0.0.1', 'ttl':120},
		{'name':'bar', 'type':'CNAME', 'content':'foo.mahtin.net'},
		{'name':'shakespeare', 'type':'TXT', 'content':"What's in a name? That which we call a rose by any other name ..."}
	]

	for dns_record in dns_records:
		r = cf.zones.dns_records.post(zone_id, data=dns_record)
	exit(0)

if __name__ == '__main__':
	main()
```

## CLI

All API calls can be called from the command line. The command will convert domain names on-the-fly into zone_identifier's.

```bash
$ cli4 [-h|--help] [-v|--verbose] [-q|--quiet] [--get|--patch|--post|-put|--delete] [item=value ...] /command...
```

For API calls that need a set of date or parameters passed there is a item=value format.
If you want a numeric value passed, then _==_ can be used to force the value to be treated as a numeric value.

The output from the CLI command is in json format (and human readable).

### Simple CLI examples

 * ```cli4 /user/billing/profile```
 * ```cli4 /user/invites```

 * ```cli4 /zones/:example.com```
 * ```cli4 /zones/:example.com/dnssec```
 * ```cli4 /zones/:example.com/settings/ipv6```
 * ```cli4 --put /zones/:example.com/activation_check```
 * ```cli4 /zones/:example.com/keyless_certificates```

 * ```cli4 /zones/:example.com/analytics/dashboard```

### More complex CLI examples

```bash
$ cli4 --delete purge_everything=true /zones/:example.com/purge_cache | jq -c .
{"id":"d8afaec3dd2b7f8c1b470e594a21a01d"}
$

$ cli4 --delete files='[http://example.com/css/styles.css]' /zones/:example.com/purge_cache | jq -c .
{"id":"d8afaec3dd2b7f8c1b470e594a21a01d"}
$

$ cli4 --delete files='[http://example.com/css/styles.css,http://example.com/js/script.js] /zones/:example.com/purge_cache | jq -c .
{"id":"d8afaec3dd2b7f8c1b470e594a21a01d"}
$

$ cli4 --delete tags='[tag1,tag2,tag3]' /zones/:example.com/purge_cache | jq -c .
cli4: /zones/:example.com/purge_cache - 1107 Only enterprise zones can purge by tag.
$
```

```bash
$ cli4 /zones/:example.com/available_plans | jq -c '.[]|{"id":.id,"name":.name}'
{"id":"a577b510288e82b26486fd1df47000ec","name":"Pro Website"}
{"id":"1ac039f6c29b691475c3d74fe588d1ae","name":"Business Website"}
{"id":"94f3b7b768b0458b56d2cac4fe5ec0f9","name":"Enterprise Website"}
{"id":"0feeeeeeeeeeeeeeeeeeeeeeeeeeeeee","name":"Free Website"}
$ 
```

### DNSSEC CLI examples

```bash
$ cli4 /zones/:example.com/dnssec | jq -c '{"status":.status}'
{"status":"disabled"}
$

$ cli4 --patch status=active /zones/:example.com/dnssec | jq -c '{"status":.status}'
{"status":"pending"}
$

$ cli4 /zones/:example.com/dnssec 
{
    "algorithm": "13", 
    "digest": "41600621c65065b09230ebc9556ced937eb7fd86e31635d0025326ccf09a7194", 
    "digest_algorithm": "SHA256", 
    "digest_type": "2", 
    "ds": "example.com. 3600 IN DS 2371 13 2 41600621c65065b09230ebc9556ced937eb7fd86e31635d0025326ccf09a7194", 
    "flags": 257, 
    "key_tag": 2371, 
    "key_type": "ECDSAP256SHA256", 
    "modified_on": "2016-05-01T22:42:15.591158Z", 
    "public_key": "mdsswUyr3DPW132mOi8V9xESWE8jTo0dxCjjnopKl+GqJxpVXckHAeF+KkxLbxILfDLUT0rAK9iUzy1L53eKGQ==", 
    "status": "pending"
}
$ 
```

## Implemented API calls

```
	GET     /user
	PATCH   /user

	GET     /user/billing/history
	GET     /user/billing/profile
	GET     /user/billing/subscriptions/apps
	GET     /user/billing/subscriptions/apps/:identifier
	GET     /user/billing/subscriptions/zones
	GET     /user/billing/subscriptions/zones/:identifier

	GET     /user/firewall/access_rules/rules
	POST    /user/firewall/access_rules/rules
	PATCH   /user/firewall/access_rules/rules/:identifier
	DELETE  /user/firewall/access_rules/rules/:identifier

	GET     /user/organizations
	GET     /user/organizations/:organization_identifier
	DELETE  /user/organizations/:organization_identifier

	GET     /user/invites
	GET     /user/invites/:identifier
	PATCH   /user/invites/:identifier

	GET     /zones
	POST    /zones
	GET     /zones/:zone_identifier
	PATCH   /zones/:zone_identifier
	DELETE  /zones/:zone_identifier

	PUT     /zones/:zone_identifier/activation_check

	GET     /zones/:zone_identifier/analytics/colos
	GET     /zones/:zone_identifier/analytics/dashboard

	GET     /zones/:zone_identifier/available_plans
	GET     /zones/:zone_identifier/available_plans/:identifier

	GET     /zones/:zone_identifier/dns_records
	POST    /zones/:zone_identifier/dns_records
	GET     /zones/:zone_identifier/dns_records/:identifier
	PUT     /zones/:zone_identifier/dns_records/:identifier
	DELETE  /zones/:zone_identifier/dns_records/:identifier

	DELETE  /zones/:zone_identifier/purge_cache

	GET     /zones/:zone_identifier/railguns
	GET     /zones/:zone_identifier/railguns/:identifier
	PATCH   /zones/:zone_identifier/railguns/:identifier
	GET     /zones/:zone_identifier/railguns/:identifier/diagnose

	GET     /zones/:zone_identifier/settings
	PATCH   /zones/:zone_identifier/settings
	GET     /zones/:zone_identifier/settings/advanced_ddos
	GET     /zones/:zone_identifier/settings/always_online
	PATCH   /zones/:zone_identifier/settings/always_online
	GET     /zones/:zone_identifier/settings/browser_cache_ttl
	PATCH   /zones/:zone_identifier/settings/browser_cache_ttl
	GET     /zones/:zone_identifier/settings/browser_check
	PATCH   /zones/:zone_identifier/settings/browser_check
	GET     /zones/:zone_identifier/settings/cache_level
	PATCH   /zones/:zone_identifier/settings/cache_level
	GET     /zones/:zone_identifier/settings/challenge_ttl
	PATCH   /zones/:zone_identifier/settings/challenge_ttl
	GET     /zones/:zone_identifier/settings/development_mode
	PATCH   /zones/:zone_identifier/settings/development_mode
	GET     /zones/:zone_identifier/settings/email_obfuscation
	PATCH   /zones/:zone_identifier/settings/email_obfuscation
	GET     /zones/:zone_identifier/settings/hotlink_protection
	PATCH   /zones/:zone_identifier/settings/hotlink_protection
	GET     /zones/:zone_identifier/settings/ip_geolocation
	PATCH   /zones/:zone_identifier/settings/ip_geolocation
	GET     /zones/:zone_identifier/settings/ipv6
	PATCH   /zones/:zone_identifier/settings/ipv6
	GET     /zones/:zone_identifier/settings/minify
	PATCH   /zones/:zone_identifier/settings/minify
	GET     /zones/:zone_identifier/settings/mirage
	PATCH   /zones/:zone_identifier/settings/mirage
	GET     /zones/:zone_identifier/settings/mobile_redirect
	PATCH   /zones/:zone_identifier/settings/mobile_redirect
	GET     /zones/:zone_identifier/settings/origin_error_page_pass_thru
	PATCH   /zones/:zone_identifier/settings/origin_error_page_pass_thru
	GET     /zones/:zone_identifier/settings/polish
	PATCH   /zones/:zone_identifier/settings/polish
	GET     /zones/:zone_identifier/settings/prefetch_preload
	PATCH   /zones/:zone_identifier/settings/prefetch_preload
	GET     /zones/:zone_identifier/settings/response_buffering
	PATCH   /zones/:zone_identifier/settings/response_buffering
	GET     /zones/:zone_identifier/settings/rocket_loader
	PATCH   /zones/:zone_identifier/settings/rocket_loader
	GET     /zones/:zone_identifier/settings/security_header
	PATCH   /zones/:zone_identifier/settings/security_header
	GET     /zones/:zone_identifier/settings/security_level
	PATCH   /zones/:zone_identifier/settings/security_level
	GET     /zones/:zone_identifier/settings/server_side_exclude
	PATCH   /zones/:zone_identifier/settings/server_side_exclude
	GET     /zones/:zone_identifier/settings/sort_query_string_for_cache
	PATCH   /zones/:zone_identifier/settings/sort_query_string_for_cache
	GET     /zones/:zone_identifier/settings/ssl
	PATCH   /zones/:zone_identifier/settings/ssl
	GET     /zones/:zone_identifier/settings/tls_1_2_only
	PATCH   /zones/:zone_identifier/settings/tls_1_2_only
	GET     /zones/:zone_identifier/settings/tls_client_auth
	PATCH   /zones/:zone_identifier/settings/tls_client_auth
	GET     /zones/:zone_identifier/settings/true_client_ip_header
	PATCH   /zones/:zone_identifier/settings/true_client_ip_header
	GET     /zones/:zone_identifier/settings/waf
	PATCH   /zones/:zone_identifier/settings/waf

	GET     /railguns
	POST    /railguns
	GET     /railguns/:identifier
	PATCH   /railguns/:identifier
	DELETE  /railguns/:identifier
	GET     /railguns/:identifier/zones

	GET     /zones/:zone_identifier/firewall/access_rules/rules
	POST    /zones/:zone_identifier/firewall/access_rules/rules
	PATCH   /zones/:zone_identifier/firewall/access_rules/rules/:identifier
	DELETE  /zones/:zone_identifier/firewall/access_rules/rules/:identifier

	GET     /zones/:zone_identifier/firewall/waf/packages/:package_identifier/rules
	GET     /zones/:zone_identifier/firewall/waf/packages/:package_identifier/rules/:identifier
	PATCH   /zones/:zone_identifier/firewall/waf/packages/:package_identifier/rules/:identifier

	GET     /zones/:zone_identifier/custom_certificates
	POST    /zones/:zone_identifier/custom_certificates
	GET     /zones/:zone_identifier/custom_certificates/:identifier
	PATCH   /zones/:zone_identifier/custom_certificates/:identifier
	DELETE  /zones/:zone_identifier/custom_certificates/:identifier
	PUT     /zones/:zone_identifier/custom_certificates/prioritize

	GET     /zones/:zone_identifier/custom_pages
	GET     /zones/:zone_identifier/custom_pages/:identifier
	PUT     /zones/:zone_identifier/custom_pages/:identifier

	GET     /zones/:zone_identifier/firewall/waf/packages
	GET     /zones/:zone_identifier/firewall/waf/packages/:identifier
	PATCH   /zones/:zone_identifier/firewall/waf/packages/:identifier
	GET     /zones/:zone_identifier/firewall/waf/packages/:package_identifier/groups
	GET     /zones/:zone_identifier/firewall/waf/packages/:package_identifier/groups/:identifier
	PATCH   /zones/:zone_identifier/firewall/waf/packages/:package_identifier/groups/:identifier

	GET     /zones/:zone_identifier/keyless_certificates
	POST    /zones/:zone_identifier/keyless_certificates
	GET     /zones/:zone_identifier/keyless_certificates/:identifier
	PATCH   /zones/:zone_identifier/keyless_certificates/:identifier
	DELETE  /zones/:zone_identifier/keyless_certificates/:identifier

	GET     /zones/:zone_identifier/pagerules
	POST    /zones/:zone_identifier/pagerules
	GET     /zones/:zone_identifier/pagerules/:identifier
	PUT     /zones/:zone_identifier/pagerules/:identifier
	PATCH   /zones/:zone_identifier/pagerules/:identifier
	DELETE  /zones/:zone_identifier/pagerules/:identifier

	GET     /organizations/:organization_identifier
	PATCH   /organizations/:organization_identifier

	GET     /organizations/:organization_identifier/members
	GET     /organizations/:organization_identifier/members/:identifier
	PATCH   /organizations/:organization_identifier/members/:identifier
	DELETE  /organizations/:organization_identifier/members/:identifier

	GET     /organizations/:organization_identifier/invites
	POST    /organizations/:organization_identifier/invites
	GET     /organizations/:organization_identifier/invites/:identifier
	PATCH   /organizations/:organization_identifier/invites/:identifier
	DELETE  /organizations/:organization_identifier/invites/:identifier

	GET     /organizations/:organization_identifier/roles
	GET     /organizations/:organization_identifier/roles/:identifier

	GET     /organizations/:organization_identifier/firewall/access_rules/rules
	POST    /organizations/:organization_identifier/firewall/access_rules/rules
	PATCH   /organizations/:organization_identifier/firewall/access_rules/rules/:identifier
	DELETE  /organizations/:organization_identifier/firewall/access_rules/rules/:identifier

	GET     /organizations/:organization_identifier/railguns
	POST    /organizations/:organization_identifier/railguns
	GET     /organizations/:organization_identifier/railguns/:identifier
	GET     /organizations/:organization_identifier/railguns/:identifier/zones
	PATCH   /organizations/:organization_identifier/railguns/:identifier
	DELETE  /organizations/:organization_identifier/railguns/:identifier

	GET     /certificates
	POST    /certificates
	GET     /certificates/:identifier
	DELETE  /certificates/:identifier

	GET     /user/virtual_dns
	POST    /user/virtual_dns
	GET     /user/virtual_dns/:identifier
	PATCH   /user/virtual_dns/:identifier
	DELETE  /user/virtual_dns/:identifier

	GET     /organizations/:organization_identifier/virtual_dns
	POST    /organizations/:organization_identifier/virtual_dns
	GET     /organizations/:organization_identifier/virtual_dns/:identifier
	PATCH   /organizations/:organization_identifier/virtual_dns/:identifier
	DELETE  /organizations/:organization_identifier/virtual_dns/:identifier

	GET     /ips
```

## Adding extra API calls manually

Extra API calls can be added via the configuration file
```bash
$ cat ~/.cloudflare/cloudflare.cfg 
[CloudFlare]
extras=
        /client/v4/command
        /client/v4/command/:command_identifier
        /client/v4/command/:command_identifier/settings
$
```

While it's easy to call anything within CloudFlare's API, it's not very useful to add items in here as they will simply return API URL errors.
Technically, this is only useful for internal testing within CloudFlare.

