# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields
from tools.translate import _


class stock_move(orm.Model):
	_inherit = ['stock.move','mail.thread']
	_name = "stock_move"