# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Manager",
    "version": "8.0.1.0.1",
    "depends": [
        "base",
        "mrp",
        "product",
        "purchase",
        "stock",
    ],
    "category": "product",
    "author": "Elico Corp",
    "url": "http://www.elico-corp.com/",
    "data": [
        'data/res_group_data.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "auto_install": False,
}
