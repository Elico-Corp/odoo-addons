# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)



{
    'name' : 'Procurement Supply Ext',
    'version' : '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'www.elico-corp.com',
    'category' : 'Generic Modules/Production',
    'depends' : ['procurement', 'sale', 'l10n_cn_apem_procurement'],
    'description': """
        Support a new field supply_method for planner to confirm it at procurement level.
        Default value is from product when confirm the sale order.
    """,
    'update_xml': [
        'procurement_supply_ext_views.xml',
    ],
    'installable': True,
    'active': False,
    'certificate': False,
}

