# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
	'name': 'Purchase Landed Costs Extended',
	'version': '7.0.1.0.0',
	'category': 'Warehouse Management',
	'depends': ['purchase', 'stock', 'account', 'purchase_landed_costs'],
	'author': 'Elico Corp',
	'license': 'AGPL-3',
	'website': 'https://www.elico-corp.com',
	'description': """

	""",
	'images': [],
	'demo': [],
	'data': ['purchase_view.xml',
	  'report/purchase_report_view.xml',
	  'wizard/landed_cost_position_invoice_view.xml',
	  'wizard/shipment_wizard_view.xml',
	  'security/ir.model.access.csv',
	  'stock_view.xml',
	  'shipment_view.xml',
	  'purchase_landed_costs_extended_data.xml'],
	'installable': True,
	'application': False
 }
