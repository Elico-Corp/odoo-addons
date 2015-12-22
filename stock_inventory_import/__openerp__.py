# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Inventory Import from CSV file",
    "version": "8.0.1.0.0",
    "category": "Generic Modules",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Daniel Campos <danielcampos@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Siyuan Gu <gu.siyuan@elico-corp.com>"
    ],
    "website": "http://www.odoomrp.com",
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_inventory_view.xml",
        "views/inventory_view.xml",
    ],
    "installable": True,
}
