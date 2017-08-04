# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

{
	"name" : "Manufacturing Order Splitting Wizard",
	"version" : "7.0.1.0.0",
	"description" : """This module adds a new wizard that allows splitting a production order into two.
	Based on the original module Developed by NaN-tic for Trod y Avia, S.L.

	This module fixed the bugs and modify the workflow of Manufacturing Order.
	Support:
	- R/M assigned, can start Manufacturing Order
	- Modifyt the QTY of R/M in the picking, then synchronize the QTY when Start Order.
	- Create a picking for produce product, link to the exist stock move.
	- When you produce the order, the picking move of produce product to be Available ,not Done.
	- When you finish the picking, then close the Manufacturing order automatically.   
	""",
	"author" : "Elico Corp",
	"website" : "https://www.elico-corp.com",
	"depends" : [ 
		'mrp', 'procurement'
	],
	"category" : "Manufacturing",
	"update_xml" : [ 
		'wizard/mro_mo_split_view.xml',
		'mrp_view.xml'
	],
	"active": False,
	"installable": True
}
