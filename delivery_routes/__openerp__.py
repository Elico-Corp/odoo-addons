# -*- encoding: utf-8 -*-
# © 2011 Cubic ERP - Teradata SAC(http://cubicerp.com)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    "name": "Delivery Routes",
    "version": "7.0.1.0.0",
    "description": """
        Manage delivery routes.
        =======================
        Based on Cubic ERP's Delivery Routes Module
        it add the following features:
        * Add group Customer Service
        * Add dts_id in purchase order, A purchase order with flag is_collected can have a delivery_route_line
        * Improve DTS , PTS. 
        * Improve Delivery carrier and driver, picker. Add color for delivery driver and picker.
        * Add interface functions with other modules sales, purchase, stock
        * use 3-seg daily dts/pts to arrange delivery.
    """,
    "author": "Elico Corp",
    "website": "https://www.elico-corp.com",
    "category": "Stock Management",
    "depends": [
            "delivery",
            "stock",
            "hr",
            #'stock_quality_control',
        ],
    "data":[
            "security/delivery_security.xml",
            "security/ir.model.access.csv",
            "wizard/fill_picking.xml",
            "wizard/select_range_view.xml",
            "delivery_view.xml",
            "delivery_sequence.xml",
            "stock_view.xml",
            "purchase_view.xml",
            "wizard/stock_view.xml",
    ],
    "demo_xml": [ ],
    "active": False,
    "installable": True,
    "certificate" : "",
    'images': [],
}

