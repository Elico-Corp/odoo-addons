# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
{
    "name" : "customer supplier default",
    "version" : "7.0.1.0.0",
    "author" : "Elico Corp",
    "website" : "https://www.elico-corp.com",
    "description": """
    * Un-select customer or supplier by default when creating contacts for companies.
    * Assign "Staff" tag to contact linked to users.
    * Make Partner Checked When Converting a quotation.
    """,
    "depends" : ['base','sale_crm'],
    "category" : "Sales",
    "update_xml" : ['customer_supplier_view.xml'],
    "license": "AGPL-3",
    "active": False,
    "installable": True
}
