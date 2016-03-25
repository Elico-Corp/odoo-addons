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
    * membership_account_balance

Usage
=====
 1. create a new payment method / account journal: VIP card
    with the check box (membership journal) checked.
 2. Go to PoS configuration and add the new payment method.
 3. Normal PoS selling.
 For more information, please check this document.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/Elico-Corp/odoo-addons/issues/new?body=module:%20pos_membership%0Aversion:%20{8.0}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Alex Duan: alex.duan@elico-corp.com

Maintainer
----------

.. image:: https://www.elico-corp.com/logo.png
:alt: Elico Corp
:target: https://www.elico-corp.com

This module is maintained by Elico Corporation.

Elico Corporation offers consulting services to implement open source management software in SMEs, with a strong involvement in quality of service.

Our headquarters are located in Shanghai with branches in Hong Kong, ShenZhen and Singapore servicing customers from Greater China, Asia Pacific, Europe, Americas, etc...
