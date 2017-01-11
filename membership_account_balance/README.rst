Membership Management - Member Account Balance
==============================================
This model adds a new type of account: membership account.
This account is a prepay account which allow member charging
their account and system can easily check the balance of their
membership account.

Technical Notes (Please ignore if you are functional)
=====================================================
 - This module total rewrites the following methods:
    * debit and credit fields compute function on model: res_partner
 - Tricks
    * This module still uses V7 API since need to overwrite some compute functions on model res_partner

Usage
-----
A new check box records the membership for the account.
(Default is not membership)

Total membership is calculated in the customer.

Contributors
------------

* Eric Caudal <eric.cauda@elico-corp.com>
* Alex Duan <alex.duan@elico-corp.com>
* Siyuan Gu: <gu.siyuan@elico-corp.com>
