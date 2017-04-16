.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================================
Membership Management - Member Account Balance
==============================================

This module extends the functionality of POS to support adds a new type of
account: membership account, and  account is a prepay account which allow member
charging, their account and system can easily check the balance of their 
membership account.

Installation
============

To install this module, you need to:

 * have basic modules installed (account, membership)

Known issues / Roadmap
======================

* This module total rewrites the following methods: debit and credit fields
  compute function on model: res_partner.
* This module still uses V7 API since need to overwrite some compute functions
  on model res_partner

Usage
-----
A new check box records the membership for the account (Default is not membership).

Total membership is calculated in the customer view.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Alex Duan <alex.duan@elico-corp.com>
* Gu SiYuan <gu.siyuan@elico-corp.com>
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