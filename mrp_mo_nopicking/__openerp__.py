# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'MO for Non Standard Manufacturing Products',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'http://www.openerp.com.cn',
    'category': 'Manufacturing',
    'sequence': 18,
    'summary': 'Manufacturing Orders with no Bill of Materials defined',
    'images': [],
    'depends': ['mrp','procurement'],
    'description': """
        Manage the Non Standard Manufacturing Product with no BoM in OpenERP
        ====================================================================

        Allows to manage the transition when implementing MRP in the project
        The module allows you to create a MO without BoM for the product.
        It will create a MO with only an incoming shipment and no error in procurement.


    """,
    'data': [
        'mrp_workflow.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

