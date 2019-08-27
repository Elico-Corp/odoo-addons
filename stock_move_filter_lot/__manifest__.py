# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock move filter lot",
    "summary": "In register lots' selection, "
               "filter lots based on their location",
    "version": "10.0.1.0.0",
    "category": "Mrp",
    "website": "https://www.elico-corp.com",
    "author": "Elico Corp",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_picking_filter_lot"
    ],
    "data": [
        "views/stock_move_views.xml"
    ]
}
