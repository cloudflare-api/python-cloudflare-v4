cloudflare-python
=================

Installation
------------

Two methods are provided to install this software. Use PyPi (see
`package <https://pypi.python.org/pypi/cloudflare>`__ details) or GitHub
(see `package <https://github.com/cloudflare/python-cloudflare>`__
details).

Via PyPI
~~~~~~~~

.. code:: bash

        $ sudo pip install cloudflare
        $

Yes - that simple! (the sudo may not be needed in some cases).

Via github
~~~~~~~~~~

.. code:: bash

        $ git clone https://github.com/cloudflare/python-cloudflare
        $ cd python-cloudflare
        $ ./setup.py build
        $ sudo ./setup.py install
        $

Or whatever variance of that you want to use.

CloudFlare API version 4
------------------------

The CloudFlare API can be found `here <https://api.cloudflare.com/>`__.
Each API call is provided via a similarly named function within the
*CloudFlare* class. A full list is provided below.

Getting Started
---------------

A very simple listing of zones within your account; including the IPv6
status of the zone.

.. code:: python

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

A more complex example follows.

.. code:: python

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

Providing CloudFlare Username and API Key
-----------------------------------------

When you create a *CloudFlare* class you can pass up to three
paramaters.

-  Account email
-  Account API key
-  Optional Debug flag (True/False)

If the account email and API key are not passed when you create the
class, then they are retreived from either the users exported shell
environment variables or the .cloudflare.cfg or ~/.cloudflare.cfg or
~/.cloudflare/cloudflare.cfg files, in that order.

There is one call that presently doesn't need any email or token
certification (the */ips* call); hence you can test without any values
saved away.

Using shell environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    $ export CF_API_EMAIL='user@example.com'
    $ export CF_API_KEY='00000000000000000000000000000000'
    $ export CF_API_CERTKEY='v1.0-...'
    $

Using configuration file to store email and keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    $ cat ~/.cloudflare/cloudflare.cfg 
    [CloudFlare]
    email = user@example.com
    token = 00000000000000000000000000000000
    certoken = v1.0-...
    $

The *CF\_API\_CERTKEY* or *certtoken* values are used for the Origin-CA
*/certificates* API calls.

Included example code
---------------------

The *examples* folder contains many examples in both simple and verbose
formats.

A DNS zone code example
-----------------------

.. code:: python

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
            {'name':'bar', 'type':'CNAME', 'content':'foo'},
            {'name':'shakespeare', 'type':'TXT', 'content':"What's in a name? That which we call a rose by any other name ..."}
        ]

        for dns_record in dns_records:
            r = cf.zones.dns_records.post(zone_id, data=dns_record)
        exit(0)

    if __name__ == '__main__':
        main()

CLI
---

All API calls can be called from the command line. The command will
convert domain names on-the-fly into zone\_identifier's.

.. code:: bash

    $ cli4 [-h|--help] [-v|--verbose] [-q|--quiet] [--get|--patch|--post|-put|--delete] [item=value ...] /command...

For API calls that need a set of date or parameters passed there is a
item=value format. If you want a numeric value passed, then *==* can be
used to force the value to be treated as a numeric value.

The output from the CLI command is in json format (and human readable).

Simple CLI examples
~~~~~~~~~~~~~~~~~~~

-  ``cli4 /user/billing/profile``
-  ``cli4 /user/invites``

-  ``cli4 /zones/:example.com``
-  ``cli4 /zones/:example.com/dnssec``
-  ``cli4 /zones/:example.com/settings/ipv6``
-  ``cli4 --put /zones/:example.com/activation_check``
-  ``cli4 /zones/:example.com/keyless_certificates``

-  ``cli4 /zones/:example.com/analytics/dashboard``

More complex CLI examples
~~~~~~~~~~~~~~~~~~~~~~~~~

Here is the creation of a DNS entry, followed by a listing of that entry
and then the deletion of that entry.

.. code:: bash

    $ $ cli4 --post name="test" type="A" content="10.0.0.1" /zones/:example.com/dns_records
    {
        "id": "94e028933c87b4bff3c70a42e6daac4f",
        "name": "test.example.com",
        "type": "A",
        "content": "10.0.0.1",
        ...
    }
    $

    $ cli4 /zones/:example.com/dns_records/:test.example.com | jq '{"id":.id,"name":.name,"type":.type,"content":.content}'
    {
      "id": "94e028933c87b4bff3c70a42e6daac4f",
      "name": "test.example.com",
      "type": "A",
      "content": "10.0.0.1"
    }

    $ cli4 --delete /zones/:example.com/dns_records/:test.example.com | jq -c .
    {"id":"94e028933c87b4bff3c70a42e6daac4f"}
    $

There's the ability to handle dns entries with multiple values. This
produces more than one API call within the command.

::

    $ cli4 /zones/:example.com/dns_records/:test.example.com | jq -c '.[]|{"id":.id,"name":.name,"type":.type,"content":.content}'
    {"id":"bca0c4a5e3691e62841627e4dc3a19ed","name":"test.example.com","type":"A","content":"192.168.0.1"}
    {"id":"d94f788e6bf72ba2a54145ad04b34f08","name":"test.example.com","type":"AAAA","content":"2001:d8b::1"}
    $

Here are the cache purging commands.

.. code:: bash

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

A somewhat useful listing of available plans for a specific zone.

.. code:: bash

    $ cli4 /zones/:example.com/available_plans | jq -c '.[]|{"id":.id,"name":.name}'
    {"id":"a577b510288e82b26486fd1df47000ec","name":"Pro Website"}
    {"id":"1ac039f6c29b691475c3d74fe588d1ae","name":"Business Website"}
    {"id":"94f3b7b768b0458b56d2cac4fe5ec0f9","name":"Enterprise Website"}
    {"id":"0feeeeeeeeeeeeeeeeeeeeeeeeeeeeee","name":"Free Website"}
    $ 

DNSSEC CLI examples
~~~~~~~~~~~~~~~~~~~

.. code:: bash

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

Implemented API calls
---------------------

+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   | ``PUT``   | ``POST``   | ``PATCH``   | ``DELETE``   | API call                                                      |
+===========+===========+============+=============+==============+===============================================================+
| ``GET``   |           | ``POST``   |             | ``DELETE``   | /certificates                                                 |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /ips                                                          |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /organizations                                                |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           | ``POST``   | ``PATCH``   | ``DELETE``   | /organizations/:identifier/firewall/access\_rules/rules       |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
|           |           |            | ``PATCH``   |              | /organizations/:identifier/invite                             |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           | ``POST``   |             | ``DELETE``   | /organizations/:identifier/invites                            |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   | ``DELETE``   | /organizations/:identifier/members                            |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           | ``POST``   | ``PATCH``   | ``DELETE``   | /organizations/:identifier/railguns                           |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /organizations/:identifier/railguns/:identifier/zones         |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /organizations/:identifier/roles                              |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           | ``POST``   | ``PATCH``   | ``DELETE``   | /organizations/:identifier/virtual\_dns                       |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           | ``POST``   | ``PATCH``   | ``DELETE``   | /railguns                                                     |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /railguns/:identifier/zones                                   |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /user                                                         |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /user/billing/history                                         |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /user/billing/profile                                         |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /user/billing/subscriptions/apps                              |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /user/billing/subscriptions/zones                             |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           | ``POST``   | ``PATCH``   | ``DELETE``   | /user/firewall/access\_rules/rules                            |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /user/invites                                                 |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             | ``DELETE``   | /user/organizations                                           |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           | ``POST``   | ``PATCH``   | ``DELETE``   | /user/virtual\_dns                                            |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           | ``POST``   | ``PATCH``   | ``DELETE``   | /zones                                                        |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
|           | ``PUT``   |            |             |              | /zones/:identifier/activation\_check                          |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /zones/:identifier/analytics/colos                            |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /zones/:identifier/analytics/dashboard                        |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /zones/:identifier/available\_plans                           |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
|           | ``PUT``   |            |             |              | /zones/:identifier/custom\_certificates/prioritize            |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           | ``POST``   | ``PATCH``   | ``DELETE``   | /zones/:identifier/custom\_certificates                       |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   | ``PUT``   |            |             |              | /zones/:identifier/custom\_pages                              |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   | ``PUT``   | ``POST``   |             | ``DELETE``   | /zones/:identifier/dns\_records                               |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/firewall/waf/packages/:identifier/groups   |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/firewall/waf/packages/:identifier/rules    |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/firewall/waf/packages                      |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           | ``POST``   | ``PATCH``   | ``DELETE``   | /zones/:identifier/firewall/access\_rules/rules               |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           | ``POST``   | ``PATCH``   | ``DELETE``   | /zones/:identifier/keyless\_certificates                      |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   | ``PUT``   | ``POST``   | ``PATCH``   | ``DELETE``   | /zones/:identifier/pagerules                                  |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
|           |           |            |             | ``DELETE``   | /zones/:identifier/purge\_cache                               |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /zones/:identifier/railguns/:identifier/diagnose              |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/railguns                                   |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings                                   |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            |             |              | /zones/:identifier/settings/advanced\_ddos                    |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/always\_online                    |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/browser\_cache\_ttl               |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/browser\_check                    |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/cache\_level                      |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/challenge\_ttl                    |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/development\_mode                 |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/email\_obfuscation                |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/hotlink\_protection               |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/ip\_geolocation                   |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/ipv6                              |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/minify                            |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/mirage                            |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/mobile\_redirect                  |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/origin\_error\_page\_pass\_thru   |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/polish                            |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/prefetch\_preload                 |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/response\_buffering               |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/rocket\_loader                    |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/security\_header                  |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/security\_level                   |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/server\_side\_exclude             |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/sort\_query\_string\_for\_cache   |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/ssl                               |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/tls\_1\_2\_only                   |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/tls\_client\_auth                 |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/true\_client\_ip\_header          |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+
| ``GET``   |           |            | ``PATCH``   |              | /zones/:identifier/settings/waf                               |
+-----------+-----------+------------+-------------+--------------+---------------------------------------------------------------+

Adding extra API calls manually
-------------------------------

Extra API calls can be added via the configuration file

.. code:: bash

    $ cat ~/.cloudflare/cloudflare.cfg 
    [CloudFlare]
    extras=
            /client/v4/command
            /client/v4/command/:command_identifier
            /client/v4/command/:command_identifier/settings
    $

While it's easy to call anything within CloudFlare's API, it's not very
useful to add items in here as they will simply return API URL errors.
Technically, this is only useful for internal testing within CloudFlare.

Issues
------

The following error can be caused by an out of date SSL/TLS library
and/or out of date Python.

::

    /usr/local/lib/python2.7/dist-packages/requests/packages/urllib3/util/ssl_.py:318: SNIMissingWarning: An HTTPS request has been made, but the SNI (Subject Name Indication) extension to TLS is not available on this platform. This may cause the server to present an incorrect TLS certificate, which can cause validation failures. You can upgrade to a newer version of Python to solve this. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#snimissingwarning.
      SNIMissingWarning
    /usr/local/lib/python2.7/dist-packages/requests/packages/urllib3/util/ssl_.py:122: InsecurePlatformWarning: A true SSLContext object is not available. This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. You can upgrade to a newer version of Python to solve this. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning.
      InsecurePlatformWarning

The solution can be found
`here <https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning>`__
and/or
`here <http://stackoverflow.com/questions/35144550/how-to-install-cryptography-on-ubuntu>`__.

Credit
------

This is based on work by `Felix Wong
(gnowxilef) <https://github.com/gnowxilef>`__ found
`here <https://github.com/cloudflare-api/python-cloudflare-v4>`__. It
has been seriously expanded upon.

Copyright
---------

Portions copyright `Felix Wong
(gnowxilef) <https://github.com/gnowxilef>`__ 2015 and CloudFlare 2016.
