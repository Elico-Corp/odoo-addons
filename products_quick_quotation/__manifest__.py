# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "Quick Quotation / Create Quotation from Products",
    "summary": "This module allows the odoo users to create Quotation from Products.",
    "version": "15.0.1",
    "description": """
        This module allows the odoo users to create Quotation from Products.
        Quick Quotation.
        Quick Quotation from Products.
        Sale Quick Quotation.
        Sale Quotation from Products.
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/products_quick_quotation.png"],
    "category": "Sales",
    "depends": [
        "base",
        "product",
        "sale",
        "purchase",
    ],
    "data": [
        "views/product_views.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "/products_quick_quotation/static/src/js/*.js",
        ],
        "web.assets_qweb": [
            "/products_quick_quotation/static/src/xml/*.xml",
        ],
    },
    "installable": True,
    "application": True,
    "price"                 :  70.00,
    "currency"              :  "EUR",
    "pre_init_hook"         :  "pre_init_check",
}
