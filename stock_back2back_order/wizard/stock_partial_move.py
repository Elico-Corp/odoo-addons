# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import time


class stock_partial_move_memory_internal(osv.osv_memory):
    _inherit = "stock.move.memory.out"
    _name = "stock.move.memory.internal"
    
class stock_partial_move(osv.osv_memory):
    _inherit = "stock.partial.move"
    _name = "stock.partial.move"
    _description = "Partial Move with Type 'internal' added."
    _columns = {
        'product_moves_internal' : fields.one2many('stock.move.memory.internal', 'wizard_id', 'Moves'),
     }


stock_partial_move()
stock_partial_move_memory_internal()
