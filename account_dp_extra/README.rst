.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================================
Separate Decimal Precision for Invoice Line
===========================================

This module corrects the following limitations in OpenERP standard modules: in standard
accounting module, all objects in the invoice line (unit price, subtotal, etc) are setup following
decimal precision given by 'Account' (eg: 2).

This module introduces a new decimal precision 'Account Line' so that you can have prices
in Invoice Line with different accuracy (eg:4)
This means that you can have 2 digits for the invoice total calculation (following your accounting 
standards) and 4 digits for the invoice details and unit price. 


Bug Tracker
===========

Bugs are tracked on `<https://github.com/Elico-Corp/openerp-7.0/issues>`_. 
In case of trouble, please check there if you issue has been already reported.
if you spotted it first,help us smash it by providing detailed and welcomed 
feedback.

Contributors
------------

* Eric Caudal <eric.caudal@elico-corp.com>
* Ian Li <ian.li@elico-corp.com>

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
