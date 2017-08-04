.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================
Manufacturing Order Splitting Wizard
====================================

This module adds a new wizard that allows splitting a production order into two.
Based on the original module Developed by NaN-tic for Trod y Avia, S.L.

This module fixed some bugs and modify the workflow of Manufacturing Order.
Support:
- R/M assigned, can start Manufacturing Order
- Modify the QTY of R/M in the picking, then synchronize the QTY when Start Order.
- Create a picking for produce product, link to the exist stock move.
- When you produce the order, the picking move of produce product to be Available ,not Done.
- When you finish the picking, then close the Manufacturing order automatically.   

Bug Tracker
===========

Bugs are tracked on `<https://github.com/Elico-Corp/openerp-7.0/issues>`_.
In case of trouble, please check there if you issue has been already reported.
if you spotted it first,help us smash it by providing detailed and welcomed 
feedback.

Contributors
------------

* Eric Caudal <eric.caudal@elico-corp.com>
* Andy Lu <andy.lu@elico-corp.com>

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
