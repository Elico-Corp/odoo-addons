# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)



{
    "name" : "Pricelists extension",
    "version" : "7.0.1.0.0",
    "author" : "Elico Corp",
	"website" : "https://www.elico-corp.com",
    "category" : "Sales",
    "depends" : ["base", "product"],
    "description": """
    This module adds a new form to be able to  directly filter and change pricelists rules.
    This is particularly useful for pricelists containing long lists of rules since the standard 
    pricelist form cannot filter rules  
    """,
    'update_xml': [
        'pricelist_extension_view.xml',
    ],
    'installable': True,
    'active': False,
}
