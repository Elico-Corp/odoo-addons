.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
Sales order and reservation process
===================================

This module extends the functionality of Website to add the reserve and change search method for website_sale.

Installation
============

To install this module, you need to:

 * have basic modules installed (theme_loftspace,website_sale,website_sale_collapse_categories)


Usage
=====
This model does the below updates for websit_sale:
 * remove the string "Taxes" in shopping cart and payment
 * Disable the "Add to cart" button and show button "Order"
    when product quantity isn't available.
 * add the description and inventory status in shopping cart page
 * add the add the description and inventory status in payment page
 * delete the product description in the shopping cart.
 * only search the product name in the search function
 * remove the odoo information in the footer

Technical Notes
===============
Inherit below template of website_forum:
 * total
 * checkout
 * product
 * cart
 * payment

In the controller/main.py, rewrite and add the below functions:
 * check_stock_inventory: check wether the product is available to sale
 * shop: rewrite the domain for the search. only keep the product name.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback

Credits
=======

Contributors
------------

* Gu SiYuan <gu.siyuan@elico-corp.com>

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
