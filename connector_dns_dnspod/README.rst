.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Connector DNS for dnspod.cn
===========================

This module allows you to manage your DNSPod domain through Odoo.
It uses the service from www.dnspod.cn and synchronizes (create/delete/update)
all relevant information such as domain names and records.
This module is based on the odoo-connector tehcnology.

Installation
============

To install this module, you need to:

 * have basic modules installed (odoo-connector framework)


Usage
=====

This module allows to manage your DNS domains through Odoo and www.dnspod.com thanks to odoo-connector

To use this module, you can:

1. Create backend link to DNSpod domain server
--------------
.. image:: https://github.com/Rona111/odoo-1/blob/10172-move-all-incubator-modules-of-elico8-to-public-github-connector_dns_dnspod/connector_dns_dnspod/static/description/dnsbackend.png?raw=true


2. Create a backend for www.dnspod.com in Odoo to allow the synchronization between Odoo and DNS provider.
-----------------
.. image:: https://github.com/Rona111/odoo-1/blob/10172-move-all-incubator-modules-of-elico8-to-public-github-connector_dns_dnspod/connector_dns_dnspod/static/description/dns8.png?raw=true
.. image:: https://github.com/Rona111/odoo-1/blob/10172-move-all-incubator-modules-of-elico8-to-public-github-connector_dns_dnspod/connector_dns_dnspod/static/description/dns11.png?raw=true

The next step is to create the DNS record you want to populate to the backend. 
Please note that the connector is split in 2 modules: 

* DNS connector to allow generic DNS management 
* DNSpod connector which allows specifically to connect to the www.dnspod.com API

3. Use Odoo to create your DNS records
---------------
.. image:: https://github.com/Rona111/odoo-1/blob/10172-move-all-incubator-modules-of-elico8-to-public-github-connector_dns_dnspod/connector_dns_dnspod/static/description/dns5.png?raw=true

Thanks to th odoo-connector technology, a job is enqueud with priority and will directly create the record in DNSPod
------------
.. image:: https://github.com/Rona111/odoo-1/blob/10172-move-all-incubator-modules-of-elico8-to-public-github-connector_dns_dnspod/connector_dns_dnspod/static/description/dns4.png?raw=true

4. When you create a domain belongs to the backend,if the domain export to the dnspod.cn successfully,the state will change to done,else exception.
----------------
.. image:: https://github.com/Rona111/odoo-1/blob/10172-move-all-incubator-modules-of-elico8-to-public-github-connector_dns_dnspod/connector_dns_dnspod/static/description/dns7.png?raw=true

5. Record can be created only in the domain which state is done. 
----------------
.. image:: https://github.com/Rona111/odoo-1/blob/10172-move-all-incubator-modules-of-elico8-to-public-github-connector_dns_dnspod/connector_dns_dnspod/static/description/dns6.png?raw=true)

6. Now You can modify record directly the DNS and records through an editable tree view..
--------------------
.. image:: https://github.com/Rona111/odoo-1/blob/10172-move-all-incubator-modules-of-elico8-to-public-github-connector_dns_dnspod/connector_dns_dnspod/static/description/dns9.png?raw=true


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/Elico-Corp/odoo/issues/new?body=module:%20connector_dns_dnspod%0Aversion:%20{8.0}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Liu Lixia <liu.lixia@elico-corp.com>
* Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
    

Maintainer
----------

.. image:: https://github.com/Rona111/odoo-1/blob/10172-move-all-incubator-modules-of-elico8-to-public-github-connector_dns_dnspod/connector_dns_dnspod/static/description/dns10.png?raw=true
.. image:: https://www.elico-corp.com/logo.png
:alt: Elico Corp
:target: https://www.elico-corp.com

This module is maintained by Elico Corporation.

Elico Corporation offers consulting services to implement open source management software in SMEs, with a strong involvement in quality of service.

Our headquarters are located in Shanghai with branches in Hong Kong, ShenZhen and Singapore servicing customers from Greater China, Asia Pacific, Europe, Americas, etc...
