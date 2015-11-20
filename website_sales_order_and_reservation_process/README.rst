website_sales_order_and_reservation_process
===========================================

This module add the reserve and change search method for website_sale.

Installation
============

To install this module, you need to:

 * have basic modules installed (website_sale)

Configuration
=============

To configure this module, you need to:

 * No specific configuration needed.

Usage
=====
This model does the below updates for websit_sale:
    * change the string "Taxes" in shopping cart and payment to "运费"
    * Disable the "Add to cart" button and show button "预定"
      when product quantity isn't available.
    * add the description and inventory status in shopping cart page
    * add the add the description and inventory status in payment page
    * only search the product name in the search function

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

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


Credits
=======


Contributors
------------

* Siyuan Gu: gu.siyuan@elico-corp.com

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization
    whose mission is to support the collaborative development of Odoo features
        and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.