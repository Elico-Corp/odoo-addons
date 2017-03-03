.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================================
Membership Management - Member Account Balance
==============================================

This module extends the functionality of POS to support adds a new type of account: membership account, and  account is a prepay account which allow member charging,their account and system can easily check the balance of their membership account.

Installation
============

To install this module, you need to:

 * have basic modules installed (account, membership)

Technical Notes (Please ignore if you are functional)
=====================================================
 - This module total rewrites the following methods:
    * debit and credit fields compute function on model: res_partner.
 - Tricks
    * This module still uses V7 API since need to
    overwrite some compute functions on model: res_partner;


Usage
-----
A new check box records the membership for the account.
(Default is not membership)

Total membership is calculated in the customer.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/Elico-Corp/odoo/issues/new?body=module:%20membership_account_balance%0Aversion:%20{8.0}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Alex Duan <alex.duan@elico-corp.com>
* Gu SiYuan <gu.siyuan@elico-corp.com>

Maintainer
----------

.. image:: https://www.elico-corp.com/logo.png
   :alt: Elico Corp
   :target: https://www.elico-corp.com
