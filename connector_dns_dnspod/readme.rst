.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Connector Dns Dnspod
=====================

This module aims to allows you to manage your DNSPod domain through Odoo.

Installation
============

To install this module, you need to:

 * have basic modules installed (connector_dns)


Usage
=====

To use this module, you need to:
1.Create a backend which links to your dnspod.cn.
2.When you create a domain belongs to the backend,if the domain export to the dnspod.cn successfully,the state will change to done,else exception.
3.Record can be created only in the domain which state is done. 

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

.. image:: https://www.elico-corp.com/logo.png
:alt: Elico Corp
:target: https://www.elico-corp.com

This module is maintained by Elico Corporation.

Elico Corporation offers consulting services to implement open source management software in SMEs, with a strong involvement in quality of service.

Our headquarters are located in Shanghai with branches in Hong Kong, ShenZhen and Singapore servicing customers from Greater China, Asia Pacific, Europe, Americas, etc...
