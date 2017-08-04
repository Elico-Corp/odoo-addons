# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Sales Quotation Improve',
    'version': '7.0.1.0.0',
    'category': 'Base',
    'description': """Sales quotation process is an important part of the
    sales process and being able to number all sales quotations and keep
    track of them is essential to the business:
    Successive new sales quotations should be stored in OpenERP.
    Related sales quotations should be linked together so that we can trace
    the history with the customer and final sales order.
    A sales order created from a sales quotation should be linked to the last
    sales quotation.
    Sales Quotations and Sales Order should have different numbering sequences.
    When a sales order is to be set as draft and revalidated (for example to
    recreate the stock pickings), original Sales Order number should be kept.
    Sales Quotation status should allow to identify in which states is a
    quotation (lost and converted).""",
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'depends': ['sale', 'sale_crm', 'sale_project', 'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/make_quotation_view.xml',
        'sale_quotation_data.xml',
        'sale_quotation_view.xml',
        'sale_order_view.xml',
        'crm_view.xml',
    ],
    'installable': True,
    'active': False,
}
