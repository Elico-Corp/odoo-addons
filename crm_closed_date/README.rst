.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================
Modify CRM Closed date to allow import
======================================

This module extends the functionality of CRM and allow modification of close date in Opportunity.
Please note that the standard behavior is kept:

* the date is updated when the opportunity stage is set as "won" (even if user changed it previously).
* the date can be manually updated by sales manager even after the opportunity stage is set as "won"

Installation
============

To install this module, you need to:

 * have basic modules installed (crm)

Usage
=====

User must install the module before importing data in the CRM in order to import the field date_closed.
Once the import is done the module can be remove (and server restarted).

Roadmap
=======

Currently the date is visible and can be changed whatever the stage which is very flexible but might be weird sometimes. We could finetune this behavior (for example the field is invisible or read-only is stage is not "won")

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Rona Lin <rona.lin@elico-corp.com>
* Eric Caudal <eric.caudal@elico-corp.com>

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
