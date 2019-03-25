.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================
Membership Management - POS Membership
======================================

This module adds new features of membership to POS:

* Introduced a new type of journal/payment method:
  VIP journal to allow member paying by his/her VIP card.
  
  Constraint: cannot pay for the membership product.
* Display the balance of the member account.

Installation
============

You need to have the following modules available:

    * membership
    * pos_pricelist (optional) -> to allow VIP members have a different price.
    * account_membership_balance

Usage
=====

#. Creates a new payment method / account journal: VIP card
    with the check box (membership journal) checked.
#. Go to PoS configuration and add the new payment method.
#. Normal PoS selling.
  


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
feedback.

Credits
=======

Contributors
------------

* Alex Duan <alex.duan@elico-corp.com>
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