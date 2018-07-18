.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
CAS Authentication
==================

This module allows users to login with their CAS account (often LDAP username
and password), and will automatically create Odoo users for them on the fly.
In Order to use it, you must have a functional CAS server already installed.


Installation
============

* Add CAS server address under Settings/General Settings
* Activate Cas Activate
* Add cas_server
* Add cas_server_port

Configuration
=============

* After installing this module, you need to configure the CAS parameters in the default settings.
* The CAS authentication only works if you are in a single database mode.
* You can launch the Odoo Server with the option --db-filter=YOUR_DATABASE to do so.


Security Considerations
=======================

Users' CAS passwords are never stored in the Odoo database, the CAS server
is queried whenever a user needs to be authenticated.
Odoo does not manage password changes in the CAS, so any change of password
should be conducted by other means.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Roméo Guillot (http://www.opensource-elanz.fr)
* Elico Corp (https://www.elico-corp.com)

Maintainer
----------

.. image:: https://www.elico-corp.com/logo.png
    :alt: Elico Corp
    :target: https://www.elico-corp.com

This module is maintained by Elico Corporation.

Elico Corp is an innovative actor in China, Hong-Kong and Singapore servicing
well known international companies and as well as local mid-sized businesses.
Since 2010, our seasoned Sino-European consultants have been providing full
range Odoo services:

* Business consultancy for Gap analysis, BPM, operational work-flows review.
* Ready-to-use ERP packages aimed at starting businesses.
* Odoo implementation for manufacturing, international trading, service industry
  and e-commerce.
* Connectors and integration with 3rd party software (Magento, Taobao, Coswin,
  Joomla, Prestashop, Tradevine etc...).
* Odoo Support services such as developments, training, maintenance and hosting.

Our headquarters are located in Shanghai with branch in Singapore servicing
customers from all over Asia Pacific.

Contact information: `Sales <contact@elico-corp.com>`__
