# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Purchase Landed Costs -- Duty zones',
     'version': '7.0.1.0.0',
     'category': 'Generic Modules',
     # depends on sale_automatic_workflow because we wanna use the sale_ids on invoice.
     'depends': ['account', 'stock',
                 'purchase_landed_costs_extended',
                 'pos_anglo_saxon_accounting', 'account_anglo_saxon',
                 'sale_automatic_workflow'],
     'author': 'Elico Corp',
     'license': 'AGPL-3',
     'website': 'https://www.elico-corp.com',
     'description': """
            Modification on purchase_landed_costs:
                * no invoices created for landed cost any more when the po confirmed.

            Limitations:
                *
    """,
     'images': [],
     'demo': [],
     'data': [
         'security/landed_cost_security.xml',
         'security/ir.model.access.csv',
         'wizard/historic_prices_view.xml',
         'wizard/stock_change_standard_price_view.xml',
         'wizard/generate_invoice_from_picking_view.xml',
         'stock_view.xml',
         # 'stock_landed_costs_data.xml'
         'product_view.xml'],
     'installable': True,
     'application': False,
    }
